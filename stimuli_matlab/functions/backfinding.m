function backmask = backfinding(image)
%returns a binary mask with the back pixels white and the face pixels black

image(image == image(1,1)) = 1; % making the background more distinct
s = regionprops(image == 1 , 'Area', 'PixelList'); % to create the mask, check where the value is 1
blobs = [s.Area].'; % checking where blobs excist adjecent areas with pix value 1
ind = find(blobs == blobs(1)); % index these pixels 
pix = s(ind).PixelList; % finding the "pixels" it belongs to

%creating the mask
backmask = logical(full(sparse(pix(:,2), pix(:,1), 1, size(image,1), size(image,2))));