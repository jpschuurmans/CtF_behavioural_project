%%
%code for checking luminance and contrast for the stimuli


close all; clear; clc

basefolder = '/home/jschuurmans/Documents/02_recurrentSF_3T/recurrentSF_3T_CodeRepo/stimuli_matlab/';
outfolder_stim = [basefolder 'stimuli/'];
outfolder_back = [basefolder 'background/'];
load([basefolder 'CTFV1_PROC.mat'])
addpath(basefolder)

load([basefolder 'CTFV1_BLEND.mat'])

%inact faces:       imshow(imset.eq_stim{2})
%negated faces:     imshow(imset.neg_stim{1})
%scrambled faces:   imshow(imset.scr_stim{1})
%masks:             imset.mask{thetype,thesf,theim}
%background:        imset.Back_scr{theframe}

outputmat = 'CTFV1_CHECK.mat';






%% CHECK plot luminance and contrast
% check stimuli first
clear dataStimLback dataStimCback dataStimLface dataStimCface
clear vecdataStimLback vecdataStimLface vecdataStimCback vecdataStimCface

%preallocating
%dataStimLback = zeros(backgrounds,length(finalstim_backpixLC(:,1))); dataStimCback = dataStimLback; dataStimLface = dataStimLback; dataStimCface = dataStimLback;
%vecdataStimLback = zeros(length(Cond1levels),length(reshape(dataStimCface,numel(dataStimCface),1))); vecdataStimLface = vecdataStimLback; vecdataStimCback = vecdataStimLback; vecdataStimCface = vecdataStimLback;


%thestim = 1; %stim, maskLSF, maskHSF
for thestim = 1:length(stimuli)
    for thetype = 1:length(Cond1levels) % intact, negated and scrambled
        for theback = 1:backgrounds %for all scrambled backgrounds
            dataStimLback(theback,:) = finalstim_backpixLC{theback,thetype,thestim}(:,1);
            dataStimCback(theback,:) = finalstim_backpixLC{theback,thetype,thestim}(:,2);
            dataStimLface(theback,:) = finalstim_facepixLC{theback,thetype,thestim}(:,1);
            dataStimCface(theback,:) = finalstim_facepixLC{theback,thetype,thestim}(:,2);
        end
    
        vecdataStimLback(thetype,:) = reshape(dataStimLback,numel(dataStimLback),1);
        vecdataStimLface(thetype,:) = reshape(dataStimLface,numel(dataStimLface),1);
        vecdataStimCback(thetype,:) = reshape(dataStimCback,numel(dataStimCback),1);
        vecdataStimCface(thetype,:) = reshape(dataStimCface,numel(dataStimCface),1);
    end
    StimLback(thestim,:,:) = vecdataStimLback;
    StimLface(thestim,:,:) = vecdataStimLface;
    StimCback(thestim,:,:) = vecdataStimCback;
    vStimCface(thestim,:,:) = vecdataStimCface;
end


close all
colorsc = hsv(length(Cond1levels));
figure
subplot(2,2,1)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataStimLback(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
title('Luminance of back pixels across images and blocks')
legend('Intact','Negated','Scrambled')
ylim ([0.35 0.55])
text(4,0.51,'intact')
text(100,0.51,['mean: ' num2str(mean(vecdataStimLback(1,:))) ', std: ' num2str(std(vecdataStimLback(1,:)))])
text(4,0.50,'negated')
text(100,0.50,['mean: ' num2str(mean(vecdataStimLback(2,:))) ', std: ' num2str(std(vecdataStimLback(2,:)))])
text(4,0.49,'scrambled')
text(100,0.49,['mean: ' num2str(mean(vecdataStimLback(3,:))) ', std: ' num2str(std(vecdataStimLback(3,:)))])



subplot(2,2,2)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataStimLface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.35 0.55])
title('Luminance of face pixels across images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.51,'intact')
text(100,0.51,['mean: ' num2str(mean(vecdataStimLface(1,:))) ', std: ' num2str(std(vecdataStimLface(1,:)))])
text(4,0.50,'negated')
text(100,0.50,['mean: ' num2str(mean(vecdataStimLface(2,:))) ', std: ' num2str(std(vecdataStimLface(2,:)))])
text(4,0.49,'scrambled')
text(100,0.49,['mean: ' num2str(mean(vecdataStimLface(3,:))) ', std: ' num2str(std(vecdataStimLface(3,:)))])


subplot(2,2,3)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataStimCback(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.05 0.15])
title('Contrast of back pixels across images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.125,'intact')
text(100,0.125,['mean: ' num2str(mean(vecdataStimCback(1,:))) ', std: ' num2str(std(vecdataStimCback(1,:)))])
text(4,0.12,'negated')
text(100,0.12,['mean: ' num2str(mean(vecdataStimCback(2,:))) ', std: ' num2str(std(vecdataStimCback(2,:)))])
text(4,0.115,'scrambled')
text(100,0.115,['mean: ' num2str(mean(vecdataStimCback(3,:))) ', std: ' num2str(std(vecdataStimCback(3,:)))])


subplot(2,2,4)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataStimCface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.05 0.15])
title('Contrast of face pixels across images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.125,'intact')
text(100,0.125,['mean: ' num2str(mean(vecdataStimCface(1,:))) ', std: ' num2str(std(vecdataStimCface(1,:)))])
text(4,0.120,'negated')
text(100,0.120,['mean: ' num2str(mean(vecdataStimCface(2,:))) ', std: ' num2str(std(vecdataStimCface(2,:)))])
text(4,0.115,'scrambled')
text(100,0.115,['mean: ' num2str(mean(vecdataStimCface(3,:))) ', std: ' num2str(std(vecdataStimCface(3,:)))])





%% do the same for background stimuli
clear dataBackLback dataBackCback dataBackLface dataBackCface
clear vecdataBackLback vecdataBackLface vecdataBackCback

%preallocate
dataBackLback = zeros(10,length(finalbackim_backpixLC(:,1)));dataBackCback = dataBackLback; dataBackLface = dataBackLback; dataBackCface = dataBackLback;
vecdataBackLback = zeros(length(Cond1levels), length(reshape(dataBackLback,numel(dataBackLback),1))); vecdataBackLface = vecdataBackLback; vecdataBackCback = vecdataBackLback; vecdataBackCface = vecdataBackLback;

thestim = 1; %stim, maskLSF, maskHSF
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    for theback = 1:10 %for all scrambled backgrounds
        dataBackLback(theback,:) = finalbackim_backpixLC{theback,thetype,thestim}(:,1);
        dataBackCback(theback,:) = finalbackim_backpixLC{theback,thetype,thestim}(:,2);
        dataBackLface(theback,:) = finalbackim_facepixLC{theback,thetype,thestim}(:,1);
        dataBackCface(theback,:) = finalbackim_facepixLC{theback,thetype,thestim}(:,2);
    end
    vecdataBackLback(thetype,:) = reshape(dataBackLback,numel(dataBackLback),1);
    vecdataBackLface(thetype,:) = reshape(dataBackLface,numel(dataBackLface),1);
    vecdataBackCback(thetype,:) = reshape(dataBackCback,numel(dataBackCback),1);
    vecdataBackCface(thetype,:) = reshape(dataBackCface,numel(dataBackCface),1);
end

figure
subplot(2,2,1)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataBackLback(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
title('Luminance of back pixels across background images and blocks')
legend('Intact','Negated','Scrambled')
ylim ([0.35 0.55])
text(4,0.51,'intact')
text(100,0.51,['mean: ' num2str(mean(vecdataBackLback(1,:))) ', std: ' num2str(std(vecdataStimLback(1,:)))])
text(4,0.50,'negated')
text(100,0.50,['mean: ' num2str(mean(vecdataBackLback(2,:))) ', std: ' num2str(std(vecdataStimLback(2,:)))])
text(4,0.49,'scrambled')
text(100,0.49,['mean: ' num2str(mean(vecdataBackLback(3,:))) ', std: ' num2str(std(vecdataStimLback(3,:)))])



subplot(2,2,2)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataBackLface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.35 0.55])
title('Luminance of face pixels across background images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.51,'intact')
text(100,0.51,['mean: ' num2str(mean(vecdataBackLface(1,:))) ', std: ' num2str(std(vecdataStimLface(1,:)))])
text(4,0.50,'negated')
text(100,0.50,['mean: ' num2str(mean(vecdataBackLface(2,:))) ', std: ' num2str(std(vecdataStimLface(2,:)))])
text(4,0.49,'scrambled')
text(100,0.49,['mean: ' num2str(mean(vecdataBackLface(3,:))) ', std: ' num2str(std(vecdataStimLface(3,:)))])


subplot(2,2,3)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataBackCback(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.05 0.15])
title('Contrast of back pixels across background images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.125,'intact')
text(100,0.125,['mean: ' num2str(mean(vecdataBackCback(1,:))) ', std: ' num2str(std(vecdataStimCback(1,:)))])
text(4,0.12,'negated')
text(100,0.12,['mean: ' num2str(mean(vecdataBackCback(2,:))) ', std: ' num2str(std(vecdataStimCback(2,:)))])
text(4,0.115,'scrambled')
text(100,0.115,['mean: ' num2str(mean(vecdataBackCback(3,:))) ', std: ' num2str(std(vecdataStimCback(3,:)))])


subplot(2,2,4)
for thetype = 1:length(Cond1levels) % intact, negated and scrambled
    plot(vecdataBackCface(thetype,:)','-o','Color',colorsc(thetype,:))
    hold on
end
ylim ([0.05 0.15])
title('Contrast of face pixels across background images and blocks')
legend('Intact','Negated','Scrambled')
text(4,0.125,'intact')
text(100,0.125,['mean: ' num2str(mean(vecdataBackCface(1,:))) ', std: ' num2str(std(vecdataStimCface(1,:)))])
text(4,0.120,'negated')
text(100,0.120,['mean: ' num2str(mean(vecdataBackCface(2,:))) ', std: ' num2str(std(vecdataStimCface(2,:)))])
text(4,0.115,'scrambled')
text(100,0.115,['mean: ' num2str(mean(vecdataBackCface(3,:))) ', std: ' num2str(std(vecdataStimCface(3,:)))])
