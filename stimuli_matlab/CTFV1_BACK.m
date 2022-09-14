% SCRAMBLED BACKGROUND GENERATION: 
% load 20 face images (half male), keep original size (1100*1100)
%  iterative scrambling + scrambling --> imset.Back_scr set
% imset.faceindex_back indicates central pixels occupied by face pixels

close all; clear; clc

basefolder = '/home/jschuurmans/Documents/02_recurrentSF_3T/recurrentSF_3T_CodeRepo/stimuli_matlab/';
load([basefolder 'CTFV1_STIM.mat'],'LC','*back', 'imset','nim','nblockspercondition')
load([basefolder 'CTFV1_PROC.mat'])
basefolder = '/home/jschuurmans/Documents/02_recurrentSF_3T/recurrentSF_3T_CodeRepo/stimuli_matlab/';
addpath(basefolder)

outputmat = 'CTFV1_BACK.mat';

%% Measure L and C, index face/back pixels
clear paddims_back
theim=1;
stimXY = [size(imset.raw_back{theim},1), size(imset.raw_back{theim},2)];
paddims_back = max(stimXY) - min(stimXY); % make a square image of same dimensions as background

for theim = 1:length(nim)
    clear im_back
    im_back = imset.raw_back{theim} ;
    if paddims_back > 0
        im_back = padarray(im_back,[0 paddims_back/2],'replicate'); % if images are not square.
    elseif paddims_back < 0
        im_back = padarray(im_back,[paddims_back/2 0],'replicate'); % if images are not square.
    end
    clear sizeprod
    sizeprod = 1: (size(im_back,1)*size(im_back,2));
    back = cell(1,3); %preallocating
    for thechannel = 1:3 % find backrgound pixels based on the weird color given to them in e.g. Photoshop, channel by channel
        back{thechannel} = find(im_back(:,:,thechannel) == im_back(1,1,thechannel));
    end
    step1 =  intersect(back{1},back{2});
    imset.backindex_back{theim} = intersect(step1,back{3});
    imset.faceindex_back{theim} = setdiff(sizeprod',imset.backindex_back{theim}); % find face pixels
    %     length(imset.backindex_back{theim}) + length(imset.faceindex_back{theim})
    im_back = rgb2gray(im_back); % convert to gray scales
    imset.gray_back{theim} = im_back;
end
clear xySize
xySize_back = size(im_back);
im2avg_stim = zeros(length(nim),xySize_back(1),xySize_back(2));


for theim = 1:length(nim)% normalizing image
    clear im
    im_back = imset.gray_back{theim};
    facepix = im_back(imset.faceindex_back{theim}); % select face pixels
    facepix  = imadjust(facepix,[0; 1],[.1; .9]);%change the range to avoid clipping further down
    facepix = facepix - mean(facepix); % normalize face pixel values (step1)
    facepix = facepix/std(facepix); % normalize face pixel values (step2)
    %facepix = (facepix*LC(2)) + LC(1);
    fprintf('%d norm check - mean: %d - std: %d\n',theim,mean(facepix),std(facepix))
    im_back(imset.faceindex_back{theim} ) = facepix; % replace face pixels of the original image by the normalized ones
	imset.norm_back{theim}  = im_back;
    im2avg_stim(theim,:,:) = im_back;
%     imshow(imset.norm_back{theim}); pause(0.15)
end

avgface = squeeze(mean(im2avg_stim,1)); imshow(avgface)
imwrite(avgface,[basefolder 'avgface_set' num2str(theim) '.bmp'],'BMP');

%% iterative scrambling
fig_over_back_ratio = length(facepix)/prod(xySize_back); % proportion of face versus background pixels of one example face 
niter = 500; % should be several hundreds
clear iterscrface
for theim = 1:length(nim)
    scrimage = phaseScrambleImage(imset.norm_back{theim});
    combiface = scrimage;
    combiface( imset.faceindex_back{theim}) =  imset.norm_back{theim}(imset.faceindex_back{theim}) ;
    combiface(imset.backindex_back{theim}) =  scrimage(imset.backindex_back{theim}) ;
    combiface = (combiface-mean2(combiface))/std2(combiface);
    fprintf('%d iterscr - mean: %d - std: %d\n',theim,mean2(combiface),std2(combiface))
    clear scrimage
    iterscrface_stim = cell(1,niter);
    for theiter = 1:niter
        
        if theiter == 1
            interim = combiface;
        elseif theiter > 1
            interim = iterscrface_stim{theiter-1};
        end
        
        scrimage = phaseScrambleImage(interim);
        scrimage(imset.faceindex_back{theim}) = imset.norm_back{theim}(imset.faceindex_back{theim}) ;
        scrimage = (scrimage-mean2(scrimage))/std2(scrimage);
        iterscrface_stim{theiter} = scrimage;
%         imshow(iterscrface_stim{theiter},[]);
    end
    imset.iter_back{theim} = iterscrface_stim{theiter};
    %imshow(imset.iter_back{theim},[]);
end
%save([basefolder outputmat],'-v7.3')


%% background frames, phasescramble 
nscrBack = nblockspercondition; % same background noise background across conditions, one different for each block of a given condition
temp = [randperm(length(nim)) randperm(length(nim)) randperm(length(nim))]; % random selection of faces to scramble to make background
whatim = temp(1:nscrBack);
clear amplim phasim i
amplim = cell(1,nscrBack); %preallocate
phasim = cell(1,nscrBack);%preallocate
for theframe=1:nscrBack
    clear daimage
    daimage=imset.iter_back{whatim(theframe)};
    fftimage=fftshift(fft2(daimage,xySize_back(1), xySize_back(2)));
    amplim{theframe}=abs(fftimage);
    phasim{theframe}=angle(fftimage);
    clear angleV facepix
    angleV= reshape((phasim{theframe}), 1, numel(phasim{theframe}));
    angle_scr= angleV(randperm(length(angleV)));
    rphasim = reshape(angle_scr, size(daimage));
    randspect = amplim{theframe}.*exp(1i*rphasim);
    realrandspect = real(ifft2(fftshift(randspect))); %inverse FFT: note that you only keep the real and not the imagenary part of the complex nrs
    realrandspect = realrandspect - mean2(realrandspect); % normalize face pixel values (step1)
    realrandspect = realrandspect/std2(realrandspect); % normalize face pixel values (step2)
    realrandspect = (realrandspect*LC(2)) + LC(1);
    fprintf('%d norm scramb check - mean: %d - std: %d\n',theframe,mean2(realrandspect),std2(realrandspect))
    imset.Back_scr{theframe} = realrandspect;
    imshow(imset.Back_scr{theframe}); pause (0.1)
end

disp('saving..')
save([basefolder outputmat],'-v7.3')

