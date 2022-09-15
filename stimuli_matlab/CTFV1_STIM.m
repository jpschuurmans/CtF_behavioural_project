close all; clear; clc

basefolder = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/stimuli_matlab/';
%disp(['basefolder: ', basefolder])
addpath(basefolder); addpath(genpath([basefolder  'functions']));

LC = [0.45 0.1]; % desired luminance and contrast
desired_size = [500 500]; %has to be square

imagefolder = [basefolder 'celebs_all/'] ;
nim = dir([imagefolder '*.bmp']);

outputmat = 'CTFV1_STIM.mat';

%% prepare face images
%load the images
for theim = 1:length(nim)
    im_stim = double(imread([imagefolder nim(theim).name]))/256; % read
    imset.raw_stim{theim} = im_stim;
end

%get raw image size
xySize_raw = size(im_stim);
xySize_stim = [max(xySize_raw) max(xySize_raw)];
% how much padding to make image square and a desired size
paddims = (desired_size(1)-xySize_stim(1)) + (max(xySize_raw(:,1:2))-min(xySize_raw(:,1:2)));



%% padd images to make them square and the desired size
%  index face/back pixels for stimulus and set desired measure L and C

for theim = 1:length(nim)
    im_stimb = imset.raw_stim{theim};
    im_stimb = padarray(im_stimb,[round(paddims/2) round(paddims/2)],'replicate'); % pad to get the same dimensions as background image.
    im_stimb = im_stimb(1:desired_size(1),1:(desired_size));
    imset.padded{theim}  = im_stimb; 
    
    im2avg_stim(theim,:,:) = im_stimb;
    imshow(imset.padded{theim}); pause(0.05)
end

%  index face/back pixels for stimulus 
aperture = getaperture(imset.padded);
facepixindex = find(aperture == 0);
backpixindex = find(aperture == 1);

for theim = 1:length(nim)
    %normalise the images 
    im_stimb = imset.padded{theim};
    facepix = im_stimb(facepixindex); % select face pixels
    facepix  = imadjust(facepix,[0; 1],[.1; .9]);%change the range to avoid clipping further down
    facepix = facepix - mean(facepix); % normalize face pixel values (step1)
    facepix = facepix/std(facepix); % normalize face pixel values (step2)
    im_stimb(facepixindex) = facepix; % replace face pixels of the original image by the normalized ones    
    fprintf('%d norm check - mean: %d - std: %d\n',theim,mean(facepix),std(facepix))
    imset.norm_stim{theim}  = im_stimb;
    
    % set desired luminance and contrast
    % make sure that the uniform background of stimulus images is = to LC(1) (isoluminant)    
    im_stimb(facepixindex) = (facepix*LC(2)) + LC(1);
    im_stimb(backpixindex) = LC(1);
    imset.eq_stim{theim}  = im_stimb;
end

avgface = squeeze(mean(im2avg_stim,1)); imshow(avgface)
imwrite(avgface,[basefolder 'avgface_set' num2str(theim) '.bmp'],'BMP');


%% iterative scrambling -> used as background or mask (mask after filering)
% we do that so that scrambled stimuli generated later are not too contaminated by the uniform background
fig_over_back_ratio = length(facepix)/prod(desired_size); % proportion of face versus background pixels of one example face 
niter = 500; % should be several hundreds [should simulate how many iterations are necessary foramplot of intact and scrambled face area to match]

for theim = 1:length(nim)
    scrimage = phaseScrambleImage(imset.norm_stim{theim});
    combiface = scrimage;
    combiface(facepixindex) =  imset.norm_stim{theim}(facepixindex) ;
    combiface(backpixindex) =  scrimage(backpixindex) ;
    combiface = (combiface-mean2(combiface))/std2(combiface);
    fprintf('%d iterative scrambling - mean: %d - std: %d\n',theim,mean(mean2(combiface)),std2(combiface))

    iterscrface_stim = cell(1,niter); %preallocation
    for theiter = 1:niter
        
        if theiter == 1
            interim = combiface;
        elseif theiter > 1
            interim = iterscrface_stim{theiter-1};
        end
        
        scrimage = phaseScrambleImage(interim);
        scrimage(facepixindex) = imset.norm_stim{theim}(facepixindex);
        scrimage = (scrimage-mean2(scrimage))/std2(scrimage);
        iterscrface_stim{theiter} = scrimage;
%         imshow(iterscrface_stim{theiter}),[]);
    end
    scrimage = phaseScrambleImage(iterscrface_stim{theiter});
    scrimage = mat2gray(scrimage);
    scrimage = (scrimage-mean2(scrimage))/std2(scrimage);
    imset.iter_back{theim} = scrimage;
%     imshow(imset.iter_stim{theim},[]);
end

%% amplitude spectrum 
%SFres = 20; % resolution of SF sampling (n SF bins) 
% the range we will work with going from 1 c/image to m*sqrt(2) c/image, m being size(im,1)
%
%for theim = 1:length(nim)
%
%    im_stim = imset.iter_stim{theim};
%    im_stim = (im_stim/std2(im_stim)) - mean2(im_stim);
%    AmpPlot_VG2(im_stim,SFres,1);% AmpPlot(im,<NoScaleBins>,<NoOrientBins>,<graphics>)
%    load([basefolder 'amplot.mat'])
%    %load('C:\Users\vgoffaux\Documents\MATLAB\amplot');
%    %     imset.SFslope{theim} = p(1);
%    SFspec.SFhist(theim,:) = AmpHist;
%    SFspec.SFslope{theim} = p;
%    SFspec.linSF{theim} = PredAmp;                                       % And the predicted amplitude based on fitted line
%     subplot(round(length(nim)/5),round(length(nim)/round(length(nim)/5)),theim)
%     loglog(exp(fineScale),PredAmp,'k-')
%     loglog(Scales,sum(AmpHist,2)','ko',exp(fineScale),PredAmp,'b-')
%      legend(sprintf('Slope of amplitude spectrum is %3.3f ',p(1)));
%end
%
%allsfslope = vertcat(SFspec.SFslope{:});
%SFspec.SFslope_ga = {mean(allsfslope,1) std(allsfslope,1)};
%SFspec.SFhist_ga = {mean(SFspec.SFhist,1) std(SFspec.SFhist,1)};
%
%
%close all; 
%set(0,'defaultlinelinewidth',3)
%lineIM = cool(length(nim));
%figure('Position', [100, 100, 1000, 1000],'Color',[1 1 1]);
%plot(log(Scales),log(SFspec.SFhist_ga{1}));
%title('Amplitude as a function of SF (log)'); xlabel('log SF (c/image)');ylabel('Amplitude');
%
%loglog(Scales,sum(AmpHist,2)','bd',exp(fineScale),PredAmp,'b-')
%
%[...] compute AUC and define LSF and HSF cutoff that energy is similar 



%% filter SF
maskcontrast = LC(2); % mask had higher contrast for masking efficiency

amplim = cell(1,length(nim)); %prealocate
phasim = cell(1,length(nim)); %prealocate
% filter intact and scrambled images
opt = struct;
opt.type = 'butt';
opt.whichfilter = 2;
%$$$$
opt.order = 3;
octwidth = 4;
maxSF=desired_size(1)/2;
gapOct = 0;

SF = [1, 2]; % two sf ranges (lsf/haf)
% sf octaves
LSFcutoff = [maxSF/(2^(octwidth*2+gapOct)) (maxSF/(2^(octwidth*2+gapOct)))*2^octwidth];
HSFcutoff = [maxSF/2^octwidth maxSF]; %4 octaves -- making 2 ranges adjecent

for theim=1:length(nim)
    daimage=imset.iter_back{theim};
    fftimage=fftshift(fft2(daimage,desired_size(1), desired_size(2)));
    amplim{theim}=abs(fftimage);
    phasim{theim}=angle(fftimage);

    for thesf = 1:length(SF) %for nr of SFs
        if thesf == 1 % first for LSF
            opt.cutoff = LSFcutoff; % LSF faces
        elseif thesf == 2 %then for HSF
            opt.cutoff = HSFcutoff; % HSF faces
        end
        
        angleV= reshape((phasim{theim}), 1, numel(phasim{theim}));
        angle_scr= angleV(randperm(length(angleV)));
        rphasim = reshape(angle_scr, size(daimage));
        randspect = amplim{theim}.*exp(1i*rphasim);
        realrandspect = real(ifft2(fftshift(randspect))); %inverse FFT: note that you only keep the real and not the imagenary part of the complex nrs
        temp = KP_SF_Filter(realrandspect,opt); %actually filtering it 
        facepix = temp(facepixindex);

        facepix = facepix - mean(facepix); % normalize face pixel values (step1)
        facepix = facepix/std(facepix); % normalize face pixel values (step2)
        facepix = (facepix*maskcontrast) + LC(1);
        fprintf('%d norm check mask - mean: %d - std: %d\n',theim,mean(facepix),std(facepix)) % check normalization worked
        
        realrandspect(facepixindex) = facepix; % replace face pixels of the original image by the normalized ones
        realrandspect(backpixindex) = LC(1); % isoluminant background

        imset.mask{thesf,theim} = realrandspect; %%%%%%%%%%%%%%%%%%%% Images to use as mask stimuli
        imshow(imset.mask{thesf,theim}); pause (0.05)
    end
end
      
close all
fig = figure('Color',[LC(1) LC(1) LC(1)]);
subplot(2,2,1)
imshow(imset.eq_stim{1})
title('Full-spectrum face stimulus')
subplot(2,2,2)
imshow(imset.iter_back{1},[])
title('Full-spectrum background')
subplot(2,2,3)
imshow(imset.mask{1,1})
title('Low spatial frquency mask')
subplot(2,2,4)
imshow(imset.mask{2,1})
title('High spatial frquency mask')
saveas(fig,[basefolder 'example.jpeg'])

disp('saving..')
save([basefolder outputmat],'-v7.3')
