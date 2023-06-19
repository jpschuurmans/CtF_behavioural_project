%% alpha blending the stimuli in the white noise
% one way (as close as what xpman program does):
% a weighted sum of the luminance values of each pixel of the image
% and the background. 

close all; clear; clc

basefolder = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/stimuli_matlab/';
outfolder = [basefolder 'finalstim/'];
outfolder_stim = [basefolder 'finalstim/stimuli/'];
outfolder_back = [basefolder 'finalstim/background/'];
outfolder_mask = [basefolder 'finalstim/masks/'];
load([basefolder 'CTFbeh_STIM.mat'])
addpath(basefolder)

backgrounds = 12;

outputmat = 'CTFbeh_BLEND.mat';

%%%%%%%%%%%% load this blurry mask
%%%%%%%%%%%% make sure the face is just as big as the stimuli
[MaskIm,~,MaskAlpha] = (imread([basefolder 'averageMask.png']));
%imshow(MaskAlpha)
MaskAlpha = padarray(MaskAlpha,[round(paddims/2) round(paddims/2)],'replicate'); % pad to get the same dimensions as background image.
MaskAlpha = MaskAlpha(1:desired_size(1),1:(desired_size));

MaskAlpha = single(MaskAlpha);
MaskAlpha = MaskAlpha./max(MaskAlpha(:));
imwrite(MaskAlpha,[outfolder 'alphamask.bmp'],'BMP')


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
 
greystim = (imset.eq_stim{1}*0)+LC(1);
% imshow(greyStim)
imwrite(greystim,[outfolder 'greybackground.bmp'],'BMP')

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
        %imshow(signalim)

        signalim(facepixindex) = signalim(facepixindex) - mean2(signalim(facepixindex)); %normalize blend stim part 1
        signalim(facepixindex) = signalim(facepixindex) / std2(signalim(facepixindex)); %normalize blend stim part 2
        signalim(facepixindex)	= (signalim(facepixindex)*LC(2)) + LC(1); %desired lum and contrast
        
        blendim = greystim.*(MaskAlpha) + signalim.*(1-MaskAlpha);
        %imshow(blendim)
        
        fprintf('mean: %f - std: %f - face %d for type: %s blendedddd\n',mean2(blendim),std2(blendim),theface,stimulus) % check contr and lum for the background
        imshow(blendim); pause (0.05)

        imset.blendim{thestim,theface} = blendim;     	

        finalstim_backpixLC{thestim}(theface,:) = [mean(blendim(backpixindex)) std(blendim(backpixindex))]; %%%% $$$$$$
        finalstim_facepixLC{thestim}(theface,:) = [mean(blendim(facepixindex)) std(blendim(facepixindex))]; %%%% $$$$$$

        % saving the stimuli with correct naming
        if thestim == 1
            name = [nim(theface).name];
            imwrite(blendim,[outfolder_stim name],'BMP')
        else
            name = [nim(theface).name(1:end-4) '_' stimuli{thestim} nim(theface).name(end-3:end)];
            imwrite(blendim,[outfolder_mask name],'BMP')
        end

    end

end

for theback = 1:backgrounds % for all scrambled backgrounds
    fprintf('bleding and safing images for %d background \n',theback)
    if theback < 10
        backname = ['BG0' num2str(theback)];
    else
        backname = ['BG' num2str(theback)];
    end

    backim = imset.iter_back{theback};
    backim = backim - mean2(backim); %normalize blend stim part 1
    backim = backim / std2(backim); %normalize blend stim part 2
    backim	= (backim*LC(2)) + LC(1); %desired lum and contrast

    backim = greystim.*(MaskAlpha) + backim.*(1-MaskAlpha);
    
    imshow(backim); 
    finalbackim_backpixLC{theback} = [mean(backim(backpixindex)) std(backim(backpixindex))]; %%%% $$$$$$
    finalbackim_facepixLC{theback} = [mean(backim(facepixindex)) std(backim(facepixindex))] ;%%%% $$$$$$

    imwrite(backim,[outfolder_back backname '.bmp'],'BMP')
end



%%

disp('saving..')
save([basefolder outputmat],'-v7.3')


