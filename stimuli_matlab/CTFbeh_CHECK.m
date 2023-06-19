%%
%code for checking luminance and contrast for the stimuli


close all; clear; clc

basefolder = 'C:/Users/Adminuser/Documents/03_SFmasking/Experiment/stimuli_matlab/';
outfolder_stim = [basefolder 'finalstim/stimuli/'];
outfolder_back = [basefolder 'finalstim/background/'];
load([basefolder 'CTFbeh_BLEND.mat'])
addpath(basefolder)
%inact faces:       imshow(imset.eq_stim{2})
%negated faces:     imshow(imset.neg_stim{1})
%scrambled faces:   imshow(imset.scr_stim{1})
%masks:             imset.mask{thetype,thesf,theim}
%background:        imset.Back_scr{theframe}

outputmat = 'CTFbeh_CHECK.mat';






%% CHECK plot luminance and contrast
% check stimuli first
clear dataStimLback dataStimCback dataStimLface dataStimCface
clear vecdataStimLback vecdataStimLface vecdataStimCback vecdataStimCface

%preallocating
%dataStimLback = zeros(backgrounds,length(finalstim_backpixLC(:,1))); dataStimCback = dataStimLback; dataStimLface = dataStimLback; dataStimCface = dataStimLback;
%vecdataStimLback = zeros(length(Cond1levels),length(reshape(dataStimCface,numel(dataStimCface),1))); vecdataStimLface = vecdataStimLback; vecdataStimCback = vecdataStimLback; vecdataStimCface = vecdataStimLback;


%thestim = 1; %stim, maskLSF, maskHSF
for thestim = 1:length(stimuli)
    
    dataStimLback = finalstim_backpixLC{thestim}(:,1);
    dataStimCback = finalstim_backpixLC{thestim}(:,2);
    dataStimLface = finalstim_facepixLC{thestim}(:,1);
    dataStimCface = finalstim_facepixLC{thestim}(:,2);

   
    StimLback(thestim,:) = reshape(dataStimLback,numel(dataStimLback),1);
    StimLface(thestim,:) = reshape(dataStimLface,numel(dataStimLface),1);
    StimCback(thestim,:) = reshape(dataStimCback,numel(dataStimCback),1);
    StimCface(thestim,:) = reshape(dataStimCface,numel(dataStimCface),1);
end


close all
colorsc = hsv(length(stimuli));
figure

subplot(1,2,1)
for thetype = 1:length(stimuli) % intact, negated and scrambled
    plot(StimLface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.35 0.55])
title('Luminance of face pixels across images and blocks')
legend('Stimuli','LSF mask','HSF mask')
text(4,0.51,'Stimuli')
text(20,0.51,['mean: ' num2str(mean(StimLface(1,:))) ', std: ' num2str(std(StimLface(1,:)))])
text(4,0.50,'LSF mask')
text(20,0.50,['mean: ' num2str(mean(StimLface(2,:))) ', std: ' num2str(std(StimLface(2,:)))])
text(4,0.49,'HSF mask')
text(20,0.49,['mean: ' num2str(mean(StimLface(3,:))) ', std: ' num2str(std(StimLface(3,:)))])


subplot(1,2,2)
for thetype = 1:length(stimuli) % intact, negated and scrambled
    plot(StimCface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.05 0.15])
xlim ([1 80])
title('Contrast of face pixels across images and blocks')
legend('Stimuli','LSF mask','HSF mask')
text(4,0.125,'Stimuli')
text(20,0.125,['mean: ' num2str(mean(StimCface(1,:))) ', std: ' num2str(std(StimCface(1,:)))])
text(4,0.120,'LSF mask')
text(20,0.120,['mean: ' num2str(mean(StimCface(2,:))) ', std: ' num2str(std(StimCface(2,:)))])
text(4,0.115,'HSF mask')
text(20,0.115,['mean: ' num2str(mean(StimCface(3,:))) ', std: ' num2str(std(StimCface(3,:)))])

