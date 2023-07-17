%MaskAlpha = imresize(MaskAlpha,1.2,'nearest');
%%%%%%%%%%%%%% is necessary for selecting backgroundpixels since
%%%%%%%%%%%%%% the blurrymask contains pixels in the border of
%%%%%%%%%%%%%% the outline with the same value as the background 
%making average mask for normalization of noise
function aperture = getaperture(allimages)
% allimages = imset.raw_stim;

sumImage = backfinding(allimages{1});
% imshow(sumImage)
for im = 1:length(allimages)
    sumImage = sumImage + allimages{im};
end

meanImage = sumImage / length(allimages);
% imshow(meanImage)

aperture = backfinding(meanImage);
% imshow(aperture)



