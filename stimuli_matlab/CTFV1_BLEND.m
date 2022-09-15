%% alpha blending the stimuli in the white noise
% one way (as close as what xpman program does):
% a weighted sum of the luminance values of each pixel of the image
% and the background. 

close all; clear; clc

basefolder = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/stimuli_matlab/';
outfolder_stim = [basefolder 'finalstim/stimuli/'];
outfolder_back = [basefolder 'finalstim/background/'];
outfolder_mask = [basefolder 'finalstim/masks/'];
load([basefolder 'CTFV1_STIM.mat'])
addpath(basefolder)

backgrounds = 8;

outputmat = 'CTFV1_BLEND.mat';

%%%%%%%%%%%% load this blurry mask
%%%%%%%%%%%% make sure the face is just as big as the stimuli
[MaskIm,~,MaskAlpha] = (imread([basefolder 'averageMask.png']));
%imshow(MaskAlpha)
MaskAlpha = padarray(MaskAlpha,[round(paddims/2) round(paddims/2)],'replicate'); % pad to get the same dimensions as background image.
MaskAlpha = MaskAlpha(1:desired_size(1),1:(desired_size));

MaskAlpha = single(MaskAlpha);
MaskAlpha = MaskAlpha./max(MaskAlpha(:));

ellipseBack = find(MaskAlpha == 1);
ellipseCenter = find(MaskAlpha < 1);



signalcontrast = 0.45;
alpha = 1-signalcontrast;
SNR = signalcontrast/alpha;
%LC = [0.45 0.1]; % desired luminance and contrast

stimuli = {'Stim' 'LSF' 'HSF'}; %stimuli and mask

%preallocate for speed
finalstim_backpixLC = cell(backgrounds,length(stimuli)); %preallocate
finalstim_facepixLC = cell(backgrounds,length(stimuli)); %preallocate
finalbackim_backpixLC = cell(backgrounds,length(stimuli)); %preallocate
finalbackim_facepixLC = cell(backgrounds,length(stimuli)); %preallocate

for theback = 1:backgrounds % for all scrambled backgrounds
    fprintf('bleding and safing images for %d background \n',theback)
    if theback < 10
        backname = ['BG0' num2str(theback)];
    else
        backname = ['BG' num2str(theback)];
    end

    for thestim = 1:length(stimuli) %stim, maskLSF, maskHSF
        %naming for checking and saving
        stimulus  = char(stimuli(thestim)) ;
        if thestim == 1
            set = imset.eq_stim;
            faceset = imset.eq_stim;
        else
            set = imset.mask(thestim-1,:);
            faceset = imset.eq_stim;
        end
        for theface = 1:length(nim) %for all faces


            signalim = set{theface};
            % imshow(signalim)

            backim = imset.iter_back{theback};
            backim = mat2gray(backim);
            
            backim = backim - mean2(backim); %normalize blend stim part 1
            backim = backim / std2(backim); %normalize blend stim part 2
            backim	= (backim*LC(2)) + LC(1); %desired lum and contrast
            imset.iter_back{theback} = backim;
            % imshow(backim)
            
            blendim = backim.*(MaskAlpha) + signalim.*(1-MaskAlpha);
            % imshow(blendim)

            blendim = blendim - mean2(blendim); %normalize blend stim part 1
            blendim = blendim / std2(blendim); %normalize blend stim part 2
            blendim	= (blendim*LC(2)) + LC(1); %desired lum and contrast
            fprintf('mean: %f - std: %f - face %d for type: %s blendedddd\n',mean2(blendim),std2(blendim),theface,stimulus) % check contr and lum for the background
            imshow(blendim)
            
            imset.blendim{theback,thestim,theface} = blendim;     	

            finalstim_backpixLC{theback,thestim}(theface,:) = [mean(blendim(backpixindex)) std(blendim(backpixindex))]; %%%% $$$$$$
            finalstim_facepixLC{theback,thestim}(theface,:) = [mean(blendim(facepixindex)) std(blendim(facepixindex))]; %%%% $$$$$$

            % saving the stimuli with correct naming
            if thestim == 1
                name = [backname '_' nim(theface).name];
                imwrite(blendim,[outfolder_stim name '.bmp'],'BMP')
            else
                name = [backname '_' nim(theface).name(1:end-4) '_' stimuli{thestim} nim(theface).name(end-3:end)];
                imwrite(blendim,[outfolder_mask name '.bmp'],'BMP')
            end

        end
        backim = imset.iter_back{theback};
        imshow(backim); 
        finalbackim_backpixLC{theback,thestim} = [mean(backim(backpixindex)) std(backim(backpixindex))]; %%%% $$$$$$
        finalbackim_facepixLC{theback,thestim} = [mean(backim(facepixindex)) std(backim(facepixindex))] ;%%%% $$$$$$

        imwrite(backim,[outfolder_back backname '.bmp'],'BMP')
    end
end




%%

disp('saving..')
save([basefolder outputmat],'-v7.3')


