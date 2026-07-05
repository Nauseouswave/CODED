clc; clear;close all

% Choose the required audio
[s,Fs] = audioread('AudioA.mp3');
%[s,Fs] = audioread('AudioB.mp3');
%[s,Fs] = audioread('AudioC.mp3');
try
  sound(s,Fs) % play audio
  pause(2)
catch
  disp('Audio playback unavailable in this environment, skipping.')
end
N = length(s);
ts = 1/Fs;
t = (0:N-1)/Fs;
figure
plot(t,s,'b','linewidth',0.5)
title('Time domain signal')
xlabel(' Time , sec ')
ylabel(' Amplitude ')
grid on
print('01_time_domain.png','-dpng','-r150')

% Convert to frequency domain
f = linspace(-Fs/2,Fs/2 - Fs/N,N);
XF = fftshift( fft(s) );
figure
plot(f,2*abs(XF)/N)
title('Frequency domain signal')
xlabel(' Freq , Hz')
ylabel(' Amplitude ')
print('02_frequency_domain.png','-dpng','-r150')

% maximum frequency
fmax = 8000;  % Maximum frequency corresponding to the peak in the spectrum

% low pass filter
[b1,a1]= butter(9,0.02*fmax/(Fs/2),'low');
% plot low pass filter
figure
freqz(b1,a1)
title('Frequency domain LPF')
print('03_lpf_response.png','-dpng','-r150')

% apply filters
Filteredx1 = filter(b1,a1,s);


% Compute the FFT for Filteredx1 and adjust for one-sided spectrum
N = length(Filteredx1);  % Length of the filtered signal
f = linspace(0, Fs/2, floor(N/2)+1);  % Frequency vector for one-sided spectrum
XF1 = fft(Filteredx1);
XF1 = XF1(1:floor(N/2)+1);  % Keep only the positive frequencies

% Plot the frequency domain of Filteredx1
figure
plot(f, 2*abs(XF1)/N)
title('Frequency domain of the filtered signal')
xlabel('Freq, Hz')
ylabel('Amplitude')
print('04_filtered_frequency_domain.png','-dpng','-r150')


%Play filtered signals
try
  sound(Filteredx1,Fs)
catch
  disp('Audio playback unavailable in this environment, skipping.')
end
