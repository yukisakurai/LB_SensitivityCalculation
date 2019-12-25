import numpy as np
import function as f
import fp as fp
import opt as op

pi = f.pi
k_b = f.k_b
c= f.c
h= f.h


########################### Observation Duty Cycle ##########################
DC = 0.85


#######################################################################
t=3.*365.*24.*60.*60.*0.95*0.95*DC;# 3 years ovservation time including cosmic ray loss (0.95), margin (0.95) and observation duty cycle
Freq = np.array([40., 50., 60., 68., 78., 89., 100., 119., 140., 166., 195., 235., 280, 337., 402.]);
m1=4   
n1=3
m2=2
n2=5

num=10000

############################# Optics Temperatures ################################
T_bath,T_cmb, T_hwp_LFT,T_hwp_HFT, T_apt, T_mir, T_fil, T_len, T_lens, T_baf, Tr_hwp,Tr_mir,Tr_fil,Tr_len,Tr_lens = op.Temp_Opt()
T_len = T_bath
T_horn = T_bath
Tr_len = T_baf
Tr_horn = T_baf
################################ FP parameters ##########################################
freqLFT, bandLFT, dpixLFT, npixLFT = fp.LFT_FP()
freqHFT, bandHFT, dpixHFT, npixHFT = fp.HFT_FP()

################################# Optics parameters ##########################################
#LFT
hwp_emiss_LFT, ref_hwp_LFT, pol_hwp_LFT, pol_dil_LFT = op.LFT_Hwp()
Spill_5Kenve, Spill_5Khood, Spill_20K, Apt_eff = op.LFT_Spill()
det_eff_LFT = op.LFT_Det() 

#HFT
hwp_emiss_HFT, ref_hwp_HFT, pol_hwp_HFT, pol_dil_HFT = op.HFT_Hwp() # MM-HWP
bf_HFT, Fnum_HFT = op.HFT_Apt() 
det_eff_HFT = op.HFT_Det() 
ref_horn = 0.05 # reflectance of feedhorn
emiss_L1, emiss_L2, ref_L1, ref_L2 = op.HFT_Lens()
                   
#Mirror 
epsilon, rho, rms = op.Mir()


#2K filter
t_fil, n_fil, tan_fil, ref_fil =op.Fil()

# detector lenslet
t_len, n_len, tan_len, ref_len =op.Len()
####################### LFT noise calculation ############################
p_opt_arr = np.zeros(num)
p_cmb_arr = np.zeros(num)
p_apt_arr = np.zeros(num)
p_hwp_arr = np.zeros(num)
p_lens_arr = np.zeros(num)
p_len_arr = np.zeros(num)
p_fil_arr = np.zeros(num)
p_5Kenve_arr = np.zeros(num)
p_5Khood_arr = np.zeros(num)
p_20K_arr = np.zeros(num)
nep_opt_arr = np.zeros(num)
dpdt_arr = np.zeros(num)
NETarrLFT=([[0.,0.,0.],[0.,0.,0.],[0.,0.,0.],[0.,0.,0.]])

print "Freq [GHz] , Popt [pW] , NEPph [aW/rtHz] , NEPg [aW/rtHz] , NEPread [aW/rtHz] , NEPint [aW/rtHz] , NEPext [aW/rtHz] , NEPdet [aW/rtHz] , NETdet [microK/rtHz] , NETarr [microK/rtHz] "


for i in range(0,m1):
    for j in range(0,n1):
        freq_l, freq_h = f.FreqRange(freqLFT[i][j],bandLFT[i][j])
        hwp_eff = 1. - hwp_emiss_LFT[i][j] - ref_hwp_LFT[i][j]
        spill_5Kenve = Spill_5Kenve[i][j]
        spill_5Khood = Spill_5Khood[i][j]
        spill_20K = Spill_20K[i][j]
        apt_eff = Apt_eff[i][j]
        
        for k in range(0,num):
            freq = freq_l+(freq_h - freq_l)*k/(num-1)
            pm_emiss, pm_eff, pm_loss = f.Mirror(freq*1.e9, rho, epsilon, rms)
            sm_emiss, sm_eff, sm_loss = f.Mirror(freq*1.e9, rho, epsilon, rms)
            fil_emiss, fil_eff = f.Trm(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)
            len_emiss, len_eff = f.Trm(t_len, n_len, tan_len, freq*1.e9, ref_len)


            p_cmb = f.BB(freq*1.e9,T_cmb)*hwp_eff*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            
            p_hwp = f.BB(freq*1.e9,T_hwp_LFT)*hwp_emiss_LFT[i][j]*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            p_hwp_ref = f.BB(freq*1.e9,Tr_hwp)*ref_hwp_LFT[i][j]*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            p_hwp = p_hwp + p_hwp_ref
            
            p_5Khood = f.BB(freq*1.e9,T_apt)*spill_5Khood*pm_eff*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            
            p_pm = f.BB(freq*1.e9,T_mir)*pm_emiss*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            p_pm_ref = f.BB(freq*1.e9,Tr_mir)*pm_loss*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]
            p_pm = p_pm + p_pm_ref
            
            p_sm = f.BB(freq*1.e9,T_mir)*sm_emiss*fil_eff*len_eff*det_eff_LFT[i][j]
            p_sm_ref = f.BB(freq*1.e9,Tr_mir)*sm_loss*fil_eff*len_eff*det_eff_LFT[i][j]
            p_sm = p_sm + p_sm_ref

            p_5Kenve =  f.BB(freq*1.e9,T_apt)*spill_5Kenve*fil_eff*len_eff*det_eff_LFT[i][j]
            p_20K =  f.BB(freq*1.e9,T_hwp_LFT)*spill_20K*fil_eff*len_eff*det_eff_LFT[i][j]
            
             
            p_fil = f.BB(freq*1.e9,T_fil)*fil_emiss*len_eff*det_eff_LFT[i][j]
            p_fil_ref = f.BB(freq*1.e9,Tr_fil)*ref_fil*len_eff*det_eff_LFT[i][j]
            p_fil = p_fil + p_fil_ref
            
            p_len = f.BB(freq*1.e9,T_len)*len_emiss*det_eff_LFT[i][j]
            p_len_ref = f.BB(freq*1.e9,Tr_len)*ref_len*det_eff_LFT[i][j]
            p_len = p_len + p_len_ref
            
            p_det = f.BB(freq*1.e9,T_bath)*(1-det_eff_LFT[i][j])
     
            p_opt = p_cmb + p_hwp + p_5Khood + p_pm + p_sm + p_5Kenve + p_20K + p_fil + p_len + p_det 

            eff = hwp_eff*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_LFT[i][j]*pol_hwp_LFT[i][j]*pol_dil_LFT[i][j]

            p_opt_arr[k] = p_opt
            p_cmb_arr[k] = p_cmb
            p_hwp_arr[k] = p_hwp
            p_lens_arr[k] = p_pm + p_sm
            p_fil_arr[k] = p_fil
            p_len_arr[k] = p_len
            p_5Kenve_arr[k] = p_5Kenve
            p_5Khood_arr[k] = p_5Khood
            p_20K_arr[k] = p_20K

            nep_opt = 2.*p_opt*f.h*freq*1.e9 + 2.*p_opt**2.
            nep_opt_arr[k] = nep_opt
            dpdt = f.dPdT(freq*1.e9, eff, T_cmb)
            dpdt_arr[k] = dpdt
                
        Popt = np.sum(p_opt_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Pcmb = np.sum(p_cmb_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Phwp = np.sum(p_hwp_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Papt = np.sum(p_apt_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Plens = np.sum(p_lens_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Pfil = np.sum(p_fil_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Plen = np.sum(p_len_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        P20K = np.sum(p_20K_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW

        Psat = 2.5*Popt    
       
        NEPopt =np.sqrt(np.sum(nep_opt_arr)*(freq_h-freq_l)*1.e9/num)*1.e18 # in unit of aW
        NEPth = np.sqrt(4.*k_b*Psat*1.e-12*T_bath*(3.+1.)**2./(2.*3.+3.)*(1.71**(2.*3.+3.)-1.)/((1.71**(3.+1.)-1.)**2.))*1.e18
       # NEPread = np.sqrt(0.21*(NEPopt**2.+NEPth**2.))
        NEPread = np.sqrt(Popt/0.5)*3.5
        NEPint = np.sqrt(NEPopt**2. + NEPth**2. + NEPread**2.)
        NEPext = np.sqrt(0.32)*np.sqrt(NEPint**2.)
        NEPdet = np.sqrt(NEPint**2. + NEPext**2.)
        DPDT = np.sum(dpdt_arr)*(freq_h-freq_l)*1.e9/num
        NETdet = NEPdet*1.e-18/np.sqrt(2.)/DPDT*1.e6 # in unit of microK
        NETarrLFT[i][j] = NETdet/np.sqrt(2.*npixLFT[i][j]*0.8)  

        print round(freqLFT[i][j],2)," , ",round(Popt,8)," , ",round(NEPopt,8)," , ",round(NEPth,8)," , ",round(NEPread,8)," , ",round(NEPint,8)," , ",round(NEPext,8)," , ",round(NEPdet,8)," , ",round(NETdet,8)," , ",round(NETarrLFT[i][j],8)


####################### MHFT noise calculation ############################

NETarrHFT=([[0.,0.,0.,0.,0],[0.,0.,0.,0.,0.]])

for i in range(0,m2):
    for j in range(0,n2):

        freq_l, freq_h = f.FreqRange(freqHFT[i][j],bandHFT[i][j])
        
        for k in range(0,num):
            freq = freq_l+(freq_h - freq_l)*k/(num-1)
            hwp_eff = 1.- hwp_emiss_HFT[i][j] - ref_hwp_HFT[i][j]
        
            apt_emiss, apt_eff = f.Aperture(dpixHFT[i][j]*1.e-3, bf_HFT[i][j], Fnum_HFT[i][j], freq*1.e9)
            
            pm_emiss = emiss_L1[i][j]
            sm_emiss = emiss_L2[i][j]
            pm_eff = 1. - pm_emiss - ref_L1[i][j]
            sm_eff = 1. - sm_emiss - ref_L2[i][j]
             
              
            fil_emiss, fil_eff = f.Trm(t_fil, n_fil, tan_fil, freq*1.e9, ref_fil)
            
            if (i==0): # lens coupled detetor
                len_emiss, len_eff = f.Trm(t_len, n_len, tan_len, freq*1.e9, ref_len)
                ref_len = ref_len

            else: # horn coupled detector
                len_emiss = 0.
                len_eff = 1.-ref_horn
                ref_len = ref_horn
              
            p_cmb = f.BB(freq*1.e9,T_cmb)*hwp_eff*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            
            p_hwp = f.BB(freq*1.e9,T_hwp_HFT)*hwp_emiss_HFT[i][j]*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            p_hwp_ref = f.BB(freq*1.e9,Tr_hwp)*ref_hwp_HFT[i][j]*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            p_hwp = p_hwp + p_hwp_ref
            
            p_apt = f.BB(freq*1.e9,T_apt)*apt_emiss*pm_eff*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            
            p_pm = f.BB(freq*1.e9,T_mir)*pm_emiss*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            p_pm_ref = f.BB(freq*1.e9,Tr_mir)*ref_L1[i][j]*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]
            p_pm = p_pm + p_pm_ref
            
            p_sm = f.BB(freq*1.e9,T_mir)*sm_emiss*fil_eff*len_eff*det_eff_HFT[i][j]
            p_sm_ref = f.BB(freq*1.e9,Tr_mir)*ref_L2[i][j]*fil_eff*len_eff*det_eff_HFT[i][j]
            p_sm = p_sm + p_sm_ref
            
            p_fil = f.BB(freq*1.e9,T_fil)*fil_emiss*len_eff*det_eff_HFT[i][j]
            p_fil_ref = f.BB(freq*1.e9,Tr_fil)*ref_fil*len_eff*det_eff_HFT[i][j]
            p_fil = p_fil + p_fil_ref
            
            p_len = f.BB(freq*1.e9,T_len)*len_emiss*det_eff_HFT[i][j]
            p_len_ref = f.BB(freq*1.e9,Tr_len)*ref_len*det_eff_HFT[i][j]
            p_len = p_len + p_len_ref
            
            p_det = f.BB(freq*1.e9,T_bath)*(1-det_eff_HFT[i][j])
     
            p_opt = p_cmb + p_hwp + p_apt + p_pm + p_sm + p_fil + p_len + p_det 

            eff = hwp_eff*apt_eff*pm_eff*sm_eff*fil_eff*len_eff*det_eff_HFT[i][j]*pol_hwp_HFT[i][j]*pol_dil_HFT[i][j]
                 
            p_opt_arr[k] = p_opt
            p_cmb_arr[k] = p_cmb
            p_hwp_arr[k] = p_hwp
            p_apt_arr[k] = p_apt
            p_lens_arr[k] = p_pm + p_sm
            p_fil_arr[k] = p_fil
            p_len_arr[k] = p_len

            nep_opt = 2.*p_opt*f.h*freq*1.e9 + 2.*p_opt**2.
            nep_opt_arr[k] = nep_opt
            dpdt = f.dPdT(freq*1.e9, eff, T_cmb)
            dpdt_arr[k] = dpdt
                 
        Popt = np.sum(p_opt_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Pcmb = np.sum(p_cmb_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Phwp = np.sum(p_hwp_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Papt = np.sum(p_apt_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Plens = np.sum(p_lens_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Pfil = np.sum(p_fil_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        Plen = np.sum(p_len_arr)*(freq_h-freq_l)*1.e9/num*1.e12 # in unit of pW
        
        Psat = 2.5*Popt
        
        NEPopt =np.sqrt(np.sum(nep_opt_arr)*(freq_h-freq_l)*1.e9/num)*1.e18 # in unit of aW
        NEPth = np.sqrt(4.*k_b*Psat*1.e-12*T_bath*(3.+1.)**2./(2.*3.+3.)*(1.71**(2.*3.+3.)-1.)/((1.71**(3.+1.)-1.)**2.))*1.e18
        NEPread = np.sqrt(0.21*(NEPopt**2.+NEPth**2.))
        NEPint = np.sqrt(NEPopt**2. + NEPth**2. + NEPread**2.)
        NEPext = np.sqrt(0.32)*np.sqrt(NEPint**2.)
        NEPdet = np.sqrt(NEPint**2. + NEPext**2.)
        DPDT = np.sum(dpdt_arr)*(freq_h-freq_l)*1.e9/num
        NETdet = NEPdet*1.e-18/np.sqrt(2.)/DPDT*1.e6 # in unit of microK
        NETarrHFT[i][j] = NETdet/np.sqrt(2.*npixHFT[i][j]*0.8)  


        print round(freqHFT[i][j],2)," , ",round(Popt,8)," , ",round(NEPopt,8)," , ",round(NEPth,8)," , ",round(NEPread,8)," , ",round(NEPint,8)," , ",round(NEPext,8)," , ",round(NEPdet,8)," , ",round(NETdet,8)," , ",round(NETarrHFT[i][j],8)
   

NETarr = np.zeros(15)        
NETarr[0]= NETarrLFT[0][0]; #40 GHz
NETarr[1]= NETarrLFT[1][0]; #50 GHz
NETarr[2]= NETarrLFT[0][1]; #60 GHz
  
NETarr[3]= np.sqrt(1./(1./pow(NETarrLFT[1][1],2.) + 1./pow(NETarrLFT[2][0],2.)));#68 GHz
NETarr[4]= np.sqrt(1./(1./pow(NETarrLFT[0][2],2.) + 1./pow(NETarrLFT[3][0],2.)));#78 GHz
NETarr[5]= np.sqrt(1./(1./pow(NETarrLFT[1][2],2.) + 1./pow(NETarrLFT[2][1],2.)));#89 GHz
NETarr[6]= np.sqrt(1./(1./pow(NETarrLFT[3][1],2.) + 1./pow(NETarrHFT[0][0],2.)));#100 GHz
NETarr[7]= np.sqrt(1./(1./pow(NETarrLFT[2][2],2.) + 1./pow(NETarrHFT[0][1],2.)));#119 GHz
NETarr[8]= np.sqrt(1./(1./pow(NETarrLFT[3][2],2.) + 1./pow(NETarrHFT[0][2],2.)));#140 GHz

NETarr[9]= NETarrHFT[0][3];#166 GHz
NETarr[10]= np.sqrt(1./(1./pow(NETarrHFT[0][4],2.) + 1./pow(NETarrHFT[1][0],2.)));#195 GHz
NETarr[11]= NETarrHFT[1][1];#235 GHz
NETarr[12]= NETarrHFT[1][2];#280 GHz
NETarr[13]= NETarrHFT[1][3];#335 GHz
NETarr[14]= NETarrHFT[1][4];#402 GHz

Sensitivity =  f.Sigma( NETarr, t);
Sum_sens = 0


print "Freq [GHz] , NETarr [microK/rtHz] , Sensitivity [microK -arcmin]"

for i in range (0,15):
    Sum_sens = Sum_sens + 1./(Sensitivity[i]**2.) 
    print Freq[i]," , ",round(NETarr[i],2)," , ",round(Sensitivity[i],2)   
Ave_sens = np.sqrt(1./Sum_sens)   

print "Averaged_sensitivity = ",round(Ave_sens,2)

print "T_HWP= [",T_hwp_LFT,T_hwp_HFT,"] K,", "T_stop= ",T_apt,"K, Duty cycle= ",DC," T_bath= ",T_bath

