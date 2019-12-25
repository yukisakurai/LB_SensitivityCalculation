
import numpy as np
import function as f
import fp as fp
import optBandAverage as op
import matplotlib.pyplot as plt
from scipy.integrate import quad, trapz
import bigfloat

pi = f.pi
k_b = f.k_b
c= f.c
h= f.h

confHFT=0

########################### Duty cycle ##########################
DC = 1.0


#######################################################################
t=3.*365.*24.*60.*60.*0.95*0.95*DC;# 3 years ovservation time including cosmic ray loss (0.95), margin (0.95) and sub-K cooler duty cycle
Freq = np.array([40., 50., 60., 68., 78., 89., 100., 119., 140., 166., 195., 235., 280, 337., 402.]);

n=5

num=1000
#num = 10
############################# Optics Temperatures ################################
T_bath,T_cmb, T_hwp_LFT,T_hwp_HFT, T_apt, T_mir, T_fil, T_len, T_lens, T_baf, Tr_hwp,Tr_mir,Tr_fil,Tr_len,Tr_lens = op.Temp_Opt()

T_len = T_bath
T_horn = T_bath
Tr_len = T_baf
Tr_horn = T_baf
################################ FP parameters ##########################################
freqMFT,bandMFT,dpixMFTarr, npixMFT = fp.HFT_FP()
#dpixMFT = 12.e-3



################################# Optics parameters ##########################################

#MFT HWP
hwp_emiss_MFTarr, ref_hwp_MFTarr = op.HFT_Hwp()
#LFT
#MFT Aperture
bf_MFT, Fnum_MFT = op.HFT_Apt()


                       
#Mirror 
epsilon, rho, rms = op.Mir()

#Field and Objective Lenses
lens_emiss_MFTarr1, lens_emiss_MFTarr2, ref_lens_MFT1,ref_lens_MFT2 = op.HFT_Lens()

#2K filter
t_fil, n_fil, tan_fil, ref_fil =op.Fil()

# detector lenslet
t_len, n_len, tan_len, ref_len =op.Len()

det_eff_MFT = op.HFT_Det()

####################### function definition ##################################
 #  def Popt(self, elemArr, emissArr, effArr, tempArr, freqs):
  #      effArr  = np.insert(effArr, len(effArr), [1. for f in freqs], axis=0); effArr = np.array(effArr).astype(np.float)
   #     return np.sum([np.trapz(self.ph.bbPowSpec(freqs, tempArr[i], emissArr[i]*np.prod(effArr[i+1:], axis=0)), freqs) for i in range(len(elemArr))])
  
def fp_cmb(freq):
    p_cmb= f.BB(freq*1.e9,T_cmb)*hwp_eff_MFT*f.AptEff(dpixMFT*1.e-3, bf_MFT, Fnum_MFT, freq*1.e9)*lens_eff_MFT1*lens_eff_MFT2*f.Eff(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)*f.Eff(t_len, n_len, tan_len, freq*1.e9, ref_len)*det_eff_MFT
   # p_cmb= f.BB(freq*1.e9,T_cmb)*hwp_eff_MFT
    return p_cmb

def fp_apt(freq):
    #p_apt= f.BB(freq*1.e9,T_apt)*(1.-f.AptEff(dpixMFT*1.e-3, bf_MFT, Fnum_MFT, freq*1.e9))*lens_eff_MFT1*lens_eff_MFT2*f.Eff(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)*f.Eff(t_len, n_len, tan_len, freq*1.e9, ref_len)*det_eff_MFT
    p_apt= f.BB(freq*1.e9,T_apt)*(1.-f.AptEff(dpixMFT*1.e-3, bf_MFT, Fnum_MFT, freq*1.e9))*f.Eff(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)*f.Eff(t_len, n_len, tan_len, freq*1.e9, ref_len)
   #  p_apt= f.BB(freq*1.e9,T_apt)
    return p_apt

def fp_lens2(freq):
    p_lens2= f.BB(freq*1.e9,T_mir)*(lens_emiss_MFT2 + ref_lens_MFT *f.BB(freq*1.e9, Tr_lens)/f.BB(freq*1.e9,T_lens))*f.Eff(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)*f.Eff(t_len, n_len, tan_len, freq*1.e9, ref_len)*det_eff_MFT
    return p_lens2

def fp_fil(freq):
    p_fil= f.BB(freq*1.e9,T_fil)*(f.Emiss(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)+ ref_fil*f.BB(freq*1.e9, Tr_fil)/f.BB(freq*1.e9,T_fil))*f.Eff(t_len, n_len, tan_len, freq*1.e9, ref_len)*det_eff_MFT
    return p_fil


def fp_len(freq):
    p_len= f.BB(freq*1.e9,T_len)*(f.Emiss(t_len, n_len, tan_len, freq*1.e9, ref_len)+ ref_len*f.BB(freq*1.e9, Tr_len)/f.BB(freq*1.e9,T_len))*det_eff_MFT
    return p_len

#############################################################################

for i in range(0,n):
        freq_l, freq_h = f.FreqRange(freqMFT[i],bandMFT[i])
        dpixMFT = dpixMFTarr[i]
        
        hwp_emiss_MFT = hwp_emiss_MFTarr[i]
        ref_hwp_MFT = ref_hwp_MFTarr[i]
        hwp_eff_MFT = 1. - hwp_emiss_MFT - ref_hwp_MFT

        lens_emiss_MFT1 = lens_emiss_MFTarr1[i]
        lens_eff_MFT1 = 1. - lens_emiss_MFT1 - ref_lens_MFT1

        lens_emiss_MFT2 = lens_emiss_MFTarr2[i]
        lens_eff_MFT2 = 1. - lens_emiss_MFT2 - ref_lens_MFT2
       
        
        p_cmb = fp_cmb(freqMFT[i])
     
        apt_emiss= 1.-f.AptEff(dpixMFT*1.e-3, bf_MFT, Fnum_MFT, freqMFT[i]*1.e9)
        eff_lens1= lens_eff_MFT1
        eff_lens2= lens_eff_MFT2
        eff_fil= f.Eff(t_fil, n_fil, tan_fil, freqMFT[i]*1.e9, ref_fil)
        eff_len= f.Eff(t_len, n_len, tan_len, freqMFT[i]*1.e9, ref_len)
        eff_det= det_eff_MFT
            
        
        P_cmb, P_cmb_err = quad(fp_cmb, freq_l, freq_h)
        P_apt, P_apt_err = quad(fp_apt, freq_l, freq_h)
        P_lens2, P_lens2_err = quad(fp_lens2, freq_l, freq_h)
        P_fil, P_fil_err = quad(fp_fil, freq_l, freq_h)
        P_len, P_len_err = quad(fp_len, freq_l, freq_h)
        P_cmb = P_cmb*1.e9*1.e12
        P_apt = P_apt*1.e9*1.e12*lens_eff_MFT1*lens_eff_MFT2*det_eff_MFT
    
     
        P_lens2 = P_lens2*1.e9*1.e12
        P_fil = P_fil*1.e9*1.e12
        P_len = P_len*1.e9*1.e12
      
        print round(freqMFT[i],2)," , ",P_cmb," , ",P_apt," , ",P_lens2," , ",P_fil," , ",P_len
        #print round(freqMFT[i],2)," , ",apt_emiss," , ",eff_lens1," , ",eff_lens2," , ",eff_fil," , ",eff_len," , ",eff_det
