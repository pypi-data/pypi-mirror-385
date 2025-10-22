import os
import copy
import time
import numpy as np
import traceback
from astropy.table import Table
from scipy.optimize import curve_fit
from theborg.emulator import Emulator
from doppler.spec1d import Spec1D
from dlnpyutils import utils as dln, astro
import doppler
import traceback
from . import utils

cspeed = 2.99792458e5  # speed of light in km/s

class BOSSSyn():

    # model BOSS nirspec spectra
    
    def __init__(self,spobs=None,loggrelation=False,fluxed=False,verbose=False):
        # Load the ANN models
        em1 = Emulator.read(utils.datadir()+'ann_22pars_3500-4200.pkl')
        em2 = Emulator.read(utils.datadir()+'ann_22pars_4000-5000.pkl')
        em3 = Emulator.read(utils.datadir()+'ann_22pars_4900-6000.pkl')
        self._models = [em1,em2,em3]
        self.nmodels = len(self._models)
        self.labels = self._models[0].label_names
        self.nlabels = len(self.labels)
        self._ranges = np.zeros((self.nmodels,self.nlabels,2),float)
        for i in range(self.nmodels):
            for j in range(self.nlabels):
                self._ranges[i,j,:] = [np.min(self._models[i].training_labels[:,j]),
                                       np.max(self._models[i].training_labels[:,j])]
        self._ranges[0,0,1] = 4100.0  # use 3500-4200 model up to 4100
        self._ranges[1,0,0] = 4100.0  # use 4000-5000 model from 4100 to 4950
        self._ranges[1,0,1] = 4950.0        
        self._ranges[2,0,0] = 4950.0  # use 4900-6000 model from 4950
        self.ranges = np.zeros((self.nlabels,2),float)
        self.ranges[0,0] = np.min(self._ranges[:,0,:])
        self.ranges[0,1] = np.max(self._ranges[:,0,:])        
        for i in np.arange(1,self.nlabels):
            self.ranges[i,:] = [np.max(self._ranges[:,i,0]),np.min(self._ranges[:,i,1])]
        
        # alpha element indexes
        alphaindex = []
        for i,l in enumerate(self.labels):
            if l in ['om','cam','mgm','tim','sm','sim']:
                alphaindex.append(i)
        self._alphaindex = np.array(alphaindex)
        
        # Input observed spectrum information
        if spobs is not None:
            self._spobs = spobs
        # Default observed spectrum            
        else:
            spobs = doppler.read(utils.datadir()+'spec-3586-55181-0500.fits')
            spobs.flux = np.zeros(spobs.npix)
            spobs.err = np.ones(spobs.npix)            
            self._spobs = spobs

        # Synthetic wavelengths
        npix_syn = 14001
        wsyn_air = np.arange(npix_syn)*0.5+3500.0   # air wavelengths
        self._wsyn = astro.airtovac(wsyn_air)       # to vacuum
        
        # Get logg label
        loggind, = np.where(np.char.array(self.labels).lower()=='logg')
        if len(loggind)==0:                
            raise ValueError('No logg label')
        self.loggind = loggind[0]
        # Get teff label
        teffind, = np.where(np.char.array(self.labels).lower()=='teff')
        if len(teffind)==0:
            raise ValueError('No teff label')
        self.teffind = teffind[0]
        # Get feh label
        mhind, = np.where(np.char.array(self.labels).lower()=='mh')
        if len(mhind)==0:
            raise ValueError('No mh label')
        self.mhind = mhind[0]                
        
        # Load the ANN model
        logg_model = Emulator.load(utils.datadir()+'apogeedr17_rgb_logg_ann.npz')
        self.logg_model = logg_model
        
        self.loggrelation = loggrelation
        self.fluxed = fluxed
        self.verbose = verbose
        self.fitparams = None
        self.njac = 0
        self._wobs = None
        self.fixparams = {}
        self.normalize = False
        
    def mklabels(self,pars):
        """ Make the labels array from a dictionary."""
        
        # Dictionary input
        if type(pars) is dict:
            labels = np.zeros(self.nlabels)
            for k in pars.keys():
                if k=='alpham':   # mean alpha
                    ind = self._alphaindex.copy()
                else:
                    ind, = np.where(np.array(self.labels)==k.lower())
                if len(ind)==0:
                    raise ValueError(k+' not found in labels: '+','.join(self.labels))
                labels[ind] = pars[k]
        # List or array input
        else:
            if self.fitparams is not None and len(pars) != len(self.labels):
                if len(pars) != len(self.fitparams):
                    raise ValueError('pars size not consistent with fitparams')
                labels = np.zeros(self.nlabels)
                for i in range(len(pars)):
                    ind, = np.where(np.array(self.labels)==self.fitparams[i])
                    labels[ind] = pars[i]
            else:
                labels = pars
            #if len(labels)<len(self.labels):
            #    raise ValueError('pars must have '+str(len(self.labels))+' elements')


        # Make sure labels is an array
        labels = np.array(labels)

        # Add any fixed values
        for k in self.fixparams.keys():
            if k=='alpham':
                ind = self._alphaindex.copy()
                labels[ind] = self.fixparams[k]
            else:
                ind, = np.where(np.array(self.labels)==k)
                labels[ind] = self.fixparams[k]
        
        # Get logg
        if self.loggrelation:
            logg = self.getlogg(labels)
            labels[self.loggind] = logg
            
        # Must at least have Teff and logg                
        if labels[0]<=0 or labels[1]<=0:
            raise ValueError('pars must at least have teff and logg')            
            
        return labels

    def get_best_model(self,labels):
        """ This returns the first ANN model that has the right range."""
        for m in range(self.nmodels):
            ranges = self._ranges[m,:,:]
            inside = True
            for i in range(3):
                inside &= (labels[i]>=ranges[i,0]) & (labels[i]<=ranges[i,1])
            if inside:
                return m
        return None
    
    def mkbounds(self,params):
        """ Make bounds for input parameter names."""
        bounds = [np.zeros(len(params)),np.zeros(len(params))]
        for i in range(len(params)):
            if params[i].lower()=='alpham':   # mean alpha
                ind = self._alphaindex.copy()
                bounds[0][i] = np.max(self.ranges[ind,0])+0.05
                bounds[1][i] = np.min(self.ranges[ind,1])-0.05
            else:
                ind, = np.where(np.array(self.labels)==params[i].lower())
                bounds[0][i] = self.ranges[ind,0]+0.05
                bounds[1][i] = self.ranges[ind,1]-0.05
        return bounds
                
    def inrange(self,pars):
        """ Check that the parameters are in range."""
        labels = self.mklabels(pars)
        # Get the right model to use based on input Teff/logg/feh
        modelindex = self.get_best_model(labels)
        if modelindex is None:
            return False,0,[self.ranges[0,0],self.ranges[0,1]]
        # Check other ranges
        for i in np.arange(1,self.nlabels):
            rr = [self._ranges[modelindex,i,0],self._ranges[modelindex,i,1]]
            if labels[i]<rr[0] or labels[i]>rr[1]:
                return False,i,rr
        return True,None,None

    def getlogg(self,labels):
        """ Get logg from the logg relation."""
        alpha = np.mean(np.array(labels)[self._alphaindex])
        teff = labels[self.teffind]
        mh = labels[self.mhind]
        logg = self.logg_model([teff,mh,alpha],border='extrapolate')
        logg = logg[0]
        return logg

    def printpars(self,pars,perror,names=None):
        """ Print out parameters and errors."""
        
        for i in range(len(pars)):
            if names is None:
                if self.fitparams is not None and len(pars) != self.nlabels:
                    name = self.fitparams[i]
                else:
                    name = self.labels[i]
            else:
                name = names[i]
            if i==0:
                print('{:6s}: {:10.1f} +/- {:5.2g}'.format(name,pars[i],perror[i]))
            else:
                print('{:6s}: {:10.4f} +/- {:5.3g}'.format(name,pars[i],perror[i]))

    def randompars(self,params=None,n=100):
        """ Create random parameters for initial guesses."""
        if params is None:
            params = self.labels
        nparams = len(params)
        rndpars = np.zeros((n,nparams),float)
        for i in range(nparams):
            if params[i]!='alpham':
                ind, = np.where(np.array(self.labels)==params[i])
                vmin = self.ranges[ind,0]
                vmax = self.ranges[ind,1]                
            else:
                ind = self._alphaindex.copy()
                vmin = np.max(self.ranges[ind,0])
                vmax = np.min(self.ranges[ind,1])
            vrange = vmax-vmin
            # make a small buffer
            vmin += vrange*0.01
            vrange *= 0.98
            rndpars[:,i] = np.random.rand(n)*vrange+vmin

        return rndpars
                
    def __call__(self,pars,snr=None,spobs=None,vrel=None,fluxed=None,wrange=None):
        # Get label array
        labels = self.mklabels(pars)
        # Are we making a fluxed spectrum?
        if fluxed is None:
            fluxed = self.fluxed

        # Use the stored observed vrel
        #if vrel is None and self._spobs is not None and hasattr(self._spobs,'vrel') and self._spobs.vrel is not None:
        if hasattr(self,'vrel') and self.vrel is not None:
            vrel = self.vrel
            
        # Check that the labels are in range
        flag,badindex,rr = self.inrange(labels)
        if flag==False:
            srr = '[{:.4f},{:.3f}]'.format(*rr)
            error = 'parameters out of range: '
            error += '{:s}={:.4f}'.format(self.labels[badindex],labels[badindex])
            error += ' '+srr
            if spobs is not None:
                owave = spobs.wave.copy()
            else:
                owave = self._spobs.wave.copy()
            # Trim wavelengths
            wobs = self._wobs
            if wobs is not None:
                gdw, = np.where((owave >= wobs[0]) & (owave <= wobs[1]))
                if len(gdw)<len(owave):
                    owave = owave[gdw]
            npix = len(owave)
            spmonte = Spec1D(np.zeros(npix,float)+1e30,err=np.ones(npix,float)*0.0001,
                             wave=owave)
            return spmonte
            #raise ValueError(error)
            
        # Get the right model to use based on input Teff/logg/feh
        modelindex = self.get_best_model(labels)
            
        # Wavelengths to use
        wave = self._wsyn
            
        # Get the synthetic spectrum
        flux = self._models[modelindex](labels)

        # Fluxed
        err = np.zeros(flux.shape,float)        
        if fluxed:
            m = doppler.models.get_best_model(labels[0:3])
            c = m._data[0].continuum
            fc = c(labels[0:3])
            wc = c.dispersion
            # interpolate to the wavelength array
            cont = dln.interp(wc,fc,wave,kind='quadratic')
            cont = 10**cont
            flux *= cont
            # Set flux at middle wavelength equal to (S/N)**2
            # then scale the rest by sqrt(flux)
            midw = np.mean([np.max(wave),np.min(wave)])
            _,midind = dln.closest(wave,midw)            
            if snr is not None:
                flux *= (snr**2)/flux[midind]
                snrall = np.sqrt(np.maximum(flux,0.0001))
                err = flux/snrall     # SNR = flux/err -> err=flux/SNR
                # now scale up so the middle wavelength has a flux of 10000
                factor = 10000/flux[midind]
                flux *= factor
                err *= factor
            else:
                flux *= 10000/flux[midind]
            
        # Doppler shift
        if vrel is not None and vrel != 0.0:
            redwave = wave*(1+vrel/cspeed)
            orig_flux = flux.copy()
            flux = dln.interp(redwave,flux,wave)
            err = dln.interp(redwave,err,wave)
            
        # Fix any bad error values
        bad = (err <=0) | ~np.isfinite(err)
        err[bad] = np.nanmedian(err)
            
        # Make the synthetic Spec1D object
        spsyn = Spec1D(flux,err=err,wave=wave)
        # Say it is normalized
        if fluxed==False:
            spsyn.normalized = True
            spsyn._cont = np.ones(spsyn.flux.shape)
        # Convolve to BOSS resolution and wavelength
        if spobs is None:
            spmonte = spsyn.prepare(self._spobs)
        else:
            spmonte = spsyn.prepare(spobs)
        # Add labels to spectrum object
        spmonte.labels = labels
        # Add noise
        if snr is not None:
            if fluxed:
                spmonte.flux += np.random.randn(*spmonte.err.shape)*spmonte.err
            else:
                spmonte.flux += np.random.randn(*spmonte.err.shape)*1/snr
                spmonte.err += 1/snr
        # Deal with any NaNs
        bd, = np.where(~np.isfinite(spmonte.flux))
        if len(bd)>0:
            spmonte.flux[bd] = 1.0
            spmonte.err[bd] = 1e30
            spmonte.mask[bd] = True

        # Trim wavelengths
        wobs = self._wobs
        if wobs is not None:
            gdw, = np.where((spmonte.wave >= wobs[0]) & (spmonte.wave <= wobs[1]))
            if len(gdw)<spmonte.npix:
                spmonte.flux = spmonte.flux[gdw]
                spmonte.err = spmonte.err[gdw]
                spmonte.wave = spmonte.wave[gdw]
                spmonte.mask = spmonte.mask[gdw]
                spmonte.numpix = np.array([len(gdw)])
                if spmonte._cont is not None:
                    spmonte._cont = spmonte._cont[gdw]
                spmonte.lsf.wave = spmonte.lsf.wave[gdw]
                if spmonte.lsf._sigma is not None:
                    spmonte.lsf._sigma = spmonte.lsf._sigma[gdw]

        # Run the continuum normalization procedure on the spectrum
        if self.normalize:
            spmonte.normalize()

        #import pdb; pdb.set_trace()
            
        return spmonte
    
    def model(self,wave,*pars,**kwargs):
        """ Model function for curve_fit."""
        if self.verbose:
            print('model: ',pars)
        out = self(pars,**kwargs)
        # Only return the flux
        if isinstance(out,Spec1D):
            return out.flux
        else:
            return out
        
    def jac(self,wave,*args,retmodel=False,**kwargs):
        """
        Method to return Jacobian matrix.
        This includes the contribution of the lookup table.

        Parameters
        ----------
        args : float
            Model parameter values as separate positional input parameters.
        retmodel : boolean, optional
            Return the model as well.  Default is retmodel=False.

        Returns
        -------
        if retmodel==False
        jac : numpy array
          Jacobian matrix of partial derivatives [N,Npars].
        model : numpy array
          Array of (1-D) model values for the input xdata and parameters.
          If retmodel==True, then (model,jac) are returned.

        Example
        -------

        jac = BOSSSyn.jac(wave,*pars)

        """

        fullargs = self.mklabels(args)
        
        # logg relation
        #  add a dummy logg value in
        #if self.loggrelation:
        #    fullargs = np.insert(args,self.loggind,0.0)
        #else:
        #    fullargs = args

        if self.verbose:
            print('jac: ',args)

        # Initialize jacobian matrix
        npix = len(wave)
        fjac = np.zeros((npix,len(self.fitparams)),np.float64)
        
        # Loop over parameters
        pars = np.array(copy.deepcopy(args))
        f0 = self.model(wave,*pars,**kwargs)        
        steps = np.zeros(len(self.fitparams))
        for i in range(len(self.fitparams)):
            targs = np.array(copy.deepcopy(fullargs))            
            if self.fitparams[i]=='alpham':
                step = 0.01
                ind = self._alphaindex
                alpha = np.mean(targs[ind])
                minalpha = np.min(targs[ind])
                maxalpha = np.max(targs[ind])
                # Check boundaries, if above upper boundary
                #   go the opposite way
                if maxalpha > np.min(self.ranges[ind,1]):
                    step *= -1
                steps[i] = step                    
                targs[ind] += step
            else:
                ind, = np.where(np.array(self.labels)==self.fitparams[i])
                if self.labels[ind[0]].lower()=='teff':
                    step = 10.0
                else:
                    step = 0.01
                # Check boundaries, if above upper boundary
                #   go the opposite way
                if targs[ind]>self.ranges[ind,1]:
                    step *= -1
                steps[i] = step                    
                targs[ind] += step
            f1 = self.model(wave,*targs,**kwargs)
            fjac[:,i] = (f1-f0)/steps[i]
            
        self.njac += 1
            
        return fjac
        
    
    def fit(self,spec,fitparams=None,fixparams={},loggrelation=False,normalize=False,
            initgrid=True,outlier=False,verbose=False,estimates=None,vrel=0.0):
        """
        Fit an observed spectrum with the ANN models and curve_fit.

        Parameters
        ----------
        spec : Spec1D 
           Spectrum to fit.
        fitparams : list, optional
           List of parameters to fit.  Default is all of them.
        fixparams : dict, optional
           Dictionary of parameters to hold fixed.
        loggrelation : bool, optional
           Use the logg-relation as a function of Teff/feh/alpha.
        normalize : bool, optional
           Normalize the spectrum.  Default is False.
        initgrid : bool, optional
           Use an initial grid of random parameters.  Default is True.
        outlier : bool, optional
           Do a second iteration after outlier rejection.  Default is False.
        verbose: bool, optional
           Verbose output to the screen.  Default is False.

        Returns
        -------
        tab : table
           Output table of results.

        Example
        -------

        tab = bsyn.fit(spec)

        """

        self.vrel = vrel
        spec.vrel = vrel
        if verbose:
            print('Vrel: {:.2f} km/s'.format(vrel))
            print('S/N: {:.2f}'.format(spec.snr))
        # Now normalize
        if normalize:
            if spec.normalized==False:
                spec.normalize()

        if fitparams is None:
            fitparams = self.labels
        self.fitparams = np.array(fitparams)
        nfitparams = len(fitparams)
        self.fixparams = fixparams
        
        wrange = [np.min(spec.wave),np.max(spec.wave)]
        self._wobs = wrange

        self.normalize = normalize
        
        # Make bounds
        #bounds = [np.zeros(nfitparams),np.zeros(nfitparams)]
        #for i in range(nfitparams):
        #    ind, = np.where(np.array(self.labels)==self.fitparams[i])
        #    bounds[0][i] = self.ranges[ind,0]
        #    bounds[1][i] = self.ranges[ind,1]
        bounds = self.mkbounds(fitparams)
        
        # Run set of ~100 points to get first estimate
        ngrid = 100
        if initgrid:
            
            #if loggrelation:
            #    nsample = 5
            #    tstep = np.ptp(self._ranges[:,0,:])/nsample
            #    tgrid = np.arange(nsample)*tstep+self._ranges[0,0,0]+tstep*0.5
            #    mstep = np.ptp(self._ranges[:,2,:])/nsample
            #    mgrid = np.arange(nsample)*mstep+self._ranges[0,2,0]+mstep*0.5
            #    astep = np.ptp(self._ranges[:,3,:])/nsample
            #    agrid = np.arange(nsample)*astep+self._ranges[0,3,0]+astep*0.5
            #    tgrid2d,mgrid2d,agrid2d = np.meshgrid(tgrid,mgrid,agrid)
            #    gridpars = np.vstack((tgrid2d.flatten(),mgrid2d.flatten(),agrid2d.flatten())).T
            #else:
            #    nsample = 4
            #    tstep = np.ptp(self._ranges[:,0,:])/nsample/1.1
            #    tgrid = np.arange(nsample)*tstep+self._ranges[0,0,0]+tstep*0.5
            #    gstep = np.ptp(self._ranges[:,1,:])/nsample/1.1
            #    ggrid = np.arange(nsample)*gstep+self._ranges[0,1,0]+gstep*0.5            
            #    mstep = np.ptp(self._ranges[:,2,:])/nsample/1.1
            #    mgrid = np.arange(nsample)*mstep+self._ranges[0,2,0]+mstep*0.5
            #    astep = np.ptp(self._ranges[:,3,:])/nsample/1.1
            #    agrid = np.arange(nsample)*astep+self._ranges[0,3,0]+astep*0.5
            #    tgrid2d,ggrid2d,mgrid2d,agrid2d = np.meshgrid(tgrid,ggrid,mgrid,agrid)
            #    gridpars = np.vstack((tgrid2d.flatten(),ggrid2d.flatten(),mgrid2d.flatten(),agrid2d.flatten())).T
            gridpars = self.randompars(self.fitparams,ngrid)
            if verbose:
               print('Testing an initial set of '+str(gridpars.shape[0])+' random parameters')
            
            # Make the models
            for i in range(gridpars.shape[0]):
                tpars1 = {}
                for j in range(len(self.fitparams)):
                    tpars1[self.fitparams[j]] = gridpars[i,j]
                sp1 = self(tpars1)
                if i==0:
                    synflux = np.zeros((gridpars.shape[0],sp1.size),float)
                synflux[i,:] = sp1.flux
            chisqarr = np.sum((synflux-spec.flux)**2/spec.err**2,axis=1)/spec.size
            bestind = np.argmin(chisqarr)
            estimates = gridpars[bestind,:]
        else:
            # Get initial estimates if not input
            if estimates is None:
                estimates = np.zeros(len(self.fitparams))
                ind, = np.where(np.array(self.fitparams)=='teff')
                if len(ind)>0:
                    estimates[ind] = 5000.0  # 4200
                ind, = np.where(np.array(self.fitparams)=='logg')
                if len(ind)>0:
                    estimates[ind] = 1.5               

        if verbose:
            print('Initial estimates: ',estimates)


        import pdb; pdb.set_trace()
            
        try:
            pars,pcov = curve_fit(self.model,spec.wave,spec.flux,p0=estimates,
                                  sigma=spec.err,bounds=bounds,jac=self.jac)
            perror = np.sqrt(np.diag(pcov))
            bestmodel = self.model(spec.wave,*pars)
            chisq = np.sum((spec.flux-bestmodel)**2/spec.err**2)/spec.size
            
            # Get full parameters
            fullpars = list(pars)
            fullperror = list(perror)
            names = list(self.fitparams)
            if loggrelation or self.loggrelation:
                logg = self.getlogg(self.mklabels(pars))
                fullpars.append(logg)
                fullperror.append(0.0)
                names.append('logg')
            # Add any fixed parameters
            for k in self.fixparams.keys():
                fullpars.append(self.fixparams[k])
                fullperror.append(0.0)
                names.append(k)

            if verbose:
                print('Best parameters:')
                self.printpars(fullpars,fullperror,names)
                print('Chisq: {:.3f}'.format(chisq))

            # Construct the output dictionary
            out = {'vrel':vrel,'snr':spec.snr,'pars':fullpars,'perror':fullperror,'wave':spec.wave,
                   'flux':spec.flux,'err':spec.err,'model':bestmodel,'chisq':chisq,
                   'loggrelation':loggrelation,'success':True}
            success = True
        except KeyboardInterrupt:
            return
        except:
            traceback.print_exc()
            success = False
            out = {'success':False}
            
        # Remove outliers and refit
        if success and outlier:
            diff = spec.flux-bestmodel
            med = np.median(diff)
            sig = dln.mad(diff)
            bd, = np.where(np.abs(diff) > 3*sig)
            nbd = len(bd)
            if nbd>0:
                if verbose:
                    print('Removing '+str(nbd)+' outliers and refitting')
                err = spec.err.copy()
                flux = spec.flux.copy()
                err[bd] = 1e30
                flux[bd] = bestmodel[bd]
                # Save original values
                pars0 = pars
                estimates = pars0
                # Run curve_fit
                try:
                    pars,pcov = curve_fit(self.model,spec.wave,flux,p0=estimates,
                                          sigma=err,bounds=bounds,jac=self.jac)
                    perror = np.sqrt(np.diag(pcov))
                    bestmodel = self.model(spec.wave,*pars)
                    chisq = np.sum((flux-bestmodel)**2/err**2)/len(flux)

                    # Get full parameters
                    if loggrelation:
                        fullpars = self.getlogg(pars)
                        fullperror = np.insert(perror,self.loggind,0.0)
                    else:
                        fullpars = pars
                        fullperror = perror

                    if verbose:
                        print('Best parameters:')
                        self.printpars(fullpars,fullperror)
                        print('Chisq: {:.3f}'.format(chisq))                        
                        
                    # Construct the output dictionary
                    out = {'vrel':vrel,'snr':spec.snr,'pars':fullpars,'perror':fullperror,'wave':spec.wave,
                           'flux':spec.flux,'err':spec.err,'mflux':flux,'merr':err,'noutlier':nbd,'model':bestmodel,
                           'chisq':chisq,'loggrelation':loggrelation,'success':True}
                    success = True
                except:
                    traceback.print_exc()
                    success = False
                    out = {'success':False}

        return out

            
    
def monte(params=None,nmonte=50,snr=50,initgrid=True,fluxed=False,normalize=False,verbose=True):
    """ Simple Monte Carlo test to recover elemental abundances."""

    # Initialize BOSS spectral simulation object
    bsyn = BOSSSyn(fluxed=fluxed)

    if params is None:
        params = {'teff':4000.0,'logg':2.0,'mh':0.0,'cm':0.1}

    fitparams = list(tuple(params.keys()))
    labels = list(tuple(params.keys()))
    truepars = [params[k] for k in params.keys()]
    nparams = len(fitparams)
    dt = [('ind',int),('snr',float),('truepars',float,nparams),('pars',float,nparams),
          ('perror',float,nparams),('chisq',float)]
    tab = Table(np.zeros(nmonte,dtype=np.dtype(dt)))
    for i in range(nmonte):
        print('---- Mock {:d} ----'.format(i+1))
        sp = bsyn(params,snr=snr)
        try:
            out = bsyn.fit(sp,fitparams=fitparams,initgrid=initgrid,
                           normalize=normalize,verbose=verbose)
            tab['ind'][i] = i+1
            tab['snr'][i] = out['snr']
            tab['truepars'][i] = truepars
            tab['pars'][i] = out['pars']
            tab['perror'][i] = out['perror']
            tab['chisq'][i] = out['chisq']
        except:
            traceback.print_exc()

    # Figure out the bias and rms for each parameter
    print('\nFinal Monte Carlos Results')
    print('--------------------------')
    dt = [('label',str,10),('nmonte',int),('value',float),('bias',float),('rms',float)]
    res = Table(np.zeros(nparams,dtype=np.dtype(dt)))
    gd, = np.where(tab['snr']>0)  # only use ones that succeeded
    for i in range(nparams):
        resid = tab['pars'][gd,i]-truepars[i]
        res['label'][i] = labels[i]
        res['nmonte'][i] = nmonte
        res['value'][i] = truepars[i]
        res['bias'][i] = np.median(resid)
        res['rms'][i] = np.sqrt(np.mean(resid**2))
        sdata = res['label'][i],res['value'][i],res['bias'][i],res['rms'][i]
        print('{:<7s}: value={:<10.2f} bias={:<10.3f} rms={:<10.3f}'.format(*sdata))
        
    return res,tab
    

def test():

    # Simulate fake BOSS data with ANN model
    em = Emulator.read('/Users/nidever/synspec/nodegrid/grid8/grid8_annmodel_300neurons_0.0001rate_20000steps.pkl')
    npix_syn = 22001
    wsyn = np.arange(npix_syn)*0.5+9000

    # need to convolve with the BOSS LSF

    wobs_coef = np.array([-1.51930967e-09, -5.46761333e-06,  2.39684716e+00,  8.99994494e+03])
    # 3847 pixels
    npix_obs = 3847
    wobs = np.polyval(wobs_coef,np.arange(npix_obs))
    
    spobs = Spec1D(np.zeros(npix_obs),wave=wobs,err=np.ones(npix_obs),
                   lsfpars=np.array([ 1.05094118e+00, -3.37514635e-06]),
                   lsftype='Gaussian',lsfxtype='wave')

    pars = np.array([4000.0,2.0,0.0])
    pars = np.concatenate((pars,np.zeros(25)))
    spsyn = Spec1D(em(pars),wave=wsyn,err=np.ones(npix_syn))
    spmonte = spsyn.prepare(spobs)

    # deal with any NaNs
    bd, = np.where(~np.isfinite(spmonte.flux))
    if len(bd)>0:
        spmonte.flux[bd] = 1.0
        spmonte.err[bd] = 1e30
        spmonte.mask[bd] = True

        
