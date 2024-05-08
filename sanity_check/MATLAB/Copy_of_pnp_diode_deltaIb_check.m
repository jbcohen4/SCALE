clc
clear
close all

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%  Colors %%%%%%%%%%%%%%%%%%%%%
Blue=[0,120,191]/255;
lBlue=[1,166,188]/255;
dBlue=[57,72,153]/255;
Green=[133,188,34]/255;
dGreen=[1,149,63]/255;
lRed=[254,222,237]/255;
Red=[222,1,16]/255;
dRed=[162,21,14]/255;
Orange=[245,142,3]/255;
Caramel=[206,172,100]/255;
Purple=[122,105,171]/255;
Yellow=[255,233,0]/255;
lGrey=[220 220 220]/255;
Grey=[170 170 170]/255;
dGrey=[120 120 120]/255;
ddGrey=[17 17 17]/255;
Cyan=[0 1 1];
Black=[0,0,0];
White=[1,1,1];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%% diode verify
TCAD_deltaIB=readtable('pnp_sanity_values.xlsx');
Xyce_diode1_4e11=readtable('PNP_4e11_1.txt');
Xyce_diode2_4e11=readtable('PNP_4e11_2.txt');
Xyce_2diode_4e11=readtable('PNP_4e11.txt');
Xyce_diode1_4e12=readtable('PNP_4e12_1.txt');
Xyce_diode2_4e12=readtable('PNP_4e12_2.txt');
Xyce_2diode_4e12=readtable('PNP_4e12.txt');
Xyce_diode1_1e12=readtable('PNP_1e12_1.txt');
Xyce_diode2_1e12=readtable('PNP_1e12_2.txt');
Xyce_2diode_1e12=readtable('PNP_1e12.txt');
Xyce_diode1_1e13=readtable('PNP_1e13_1.txt');
Xyce_diode2_1e13=readtable('PNP_1e13_2.txt');
Xyce_2diode_1e13=readtable('PNP_1e13.txt');


figure
semilogy(TCAD_deltaIB.Ve(1:37),TCAD_deltaIB.x403702000000(1:37),':o','Color',Black,'DisplayName','TCAD delta Ib, f=4e11');
hold on
plot(Xyce_2diode_4e11.V_1_(1:37),Xyce_2diode_4e11.x_I_D1__I_D2__(1:37),'--','Color',Orange,'DisplayName','Xyce 2 diodes, f=4e11');
plot(Xyce_diode1_4e11.V_1_(1:37),Xyce_diode1_4e11.I_D1_(1:37),'--','Color',Red,'DisplayName','Xyce 1st diode, f=4e11');


plot(TCAD_deltaIB.Ve,TCAD_deltaIB.x4037020000000,':o','Color',Cyan,'DisplayName','TCAD delta Ib, f=4e12');
plot(Xyce_2diode_4e12.V_1_,Xyce_2diode_4e12.x_I_D1__I_D2__,'--','Color',Orange,'DisplayName','Xyce 2 diodes, f=4e12');
plot(Xyce_diode1_4e12.V_1_(1:42),Xyce_diode1_4e12.I_D1_(1:42),'--','Color',Red,'DisplayName','Xyce 1st diode, f=4e12');
plot(Xyce_diode2_4e12.V_1_(47:67),Xyce_diode2_4e12.I_D1_(47:67),'--','Color',Blue,'DisplayName','Xyce 2nd diode, f=4e12');


plot(TCAD_deltaIB.Ve,TCAD_deltaIB.x1000000000000,':o','Color',Purple,'DisplayName','TCAD delta Ib, f=1e12');
plot(Xyce_2diode_1e12.V_1_,Xyce_2diode_1e12.x_I_D1__I_D2__,'--','Color',Orange,'DisplayName','Xyce 2 diodes, f=1e12');
plot(Xyce_diode1_1e12.V_1_(1:42),Xyce_diode1_1e12.I_D1_(1:42),'--','Color',Red,'DisplayName','Xyce 1st diode, f=1e12');
plot(Xyce_diode2_1e12.V_1_(47:67),Xyce_diode2_1e12.I_D1_(47:67),'--','Color',Blue,'DisplayName','Xyce 2nd diode, f=1e12');

plot(TCAD_deltaIB.Ve,TCAD_deltaIB.x10000000000000,':o','Color',Green,'DisplayName','TCAD delta Ib, f=1e13');
plot(Xyce_2diode_1e13.V_1_,Xyce_2diode_1e13.x_I_D1__I_D2__,'--','Color',Orange,'DisplayName','Xyce 2 diodes, f=1e13');
plot(Xyce_diode1_1e13.V_1_(1:42),Xyce_diode1_1e13.I_D1_(1:42),'--','Color',Red,'DisplayName','Xyce 1st diode, f=1e13');
plot(Xyce_diode2_1e13.V_1_(47:67),Xyce_diode2_1e13.I_D1_(47:67),'--','Color',Blue,'DisplayName','Xyce 2nd diode, f=1e13');


hold off
xlim([0.2 0.8]);
ylim([0.2e-12 0.2e-2]);
title('PNP Diode Sanity Check');
xlabel('Voltage');
ylabel('Current (A)');
legend('Location','best')
set(gca,'FontSize',24)
grid on
x0=100;
y0=50;
width=650;
height=500;
set(legend,'Fontsize',12)
set(gcf,'units','points','position',[x0,y0,width,height]);
set(gcf,'color','w');
print('TCAD_deltaIb_Xyce_diode','-dpng','-r300')


