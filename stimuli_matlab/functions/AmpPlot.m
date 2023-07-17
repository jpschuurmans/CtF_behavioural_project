% [AmpHist]=AmpPlot(im,<NoScaleBins>,<NoOrientBins>,<graphics>)
%
% Computes Fourier amplitude binned by orientation and spatial freqeuncy.
% Give it an image ('im') and (optionally) the number of bins for SF and
% orientation. It returns a matrix of the power. Note that it excludes d.c.
%
% e.g. AmpHist=AmpPlot(randn(256),11,8,1);
%
% Waning. Although this way of plotting amplitude as a function of orientation
% does take into account sampling (on the pixel-raster) to properly measure
% ansiotropies i recommend randomly rotating the image,  making multiple
% measurements, correcting for the rotation and pooling. 
%
% by Steven Dakin (s.dakin@ucl.ac.uk, UCL IoO, Feb 2009)
%
function [AmpHist]=AmpPlot(im,varargin) 

[m n]                 = size(im);                                               % Image dimensions
f1                      = fftshift(abs(fft2(double(im))));              % Computes ampltidue spectrum
[X Y A B]           = MakeMesh(m,n);                                 % These meshs are sued to define the bins

% Set defaults. Scale bins in half octave steps, only one orientation bin, graphics on
NoScaleBins=2*log(m)/log(2)-1;  NoOrientBins=1; graphics=1;
switch nargin
    case 2, NoScaleBins=varargin{1};           
    case 3, NoScaleBins=varargin{1};           NoOrientBins=varargin{2};    
    case 4, NoScaleBins=varargin{1};           NoOrientBins=varargin{2};    graphics=varargin{3};
end
if NoOrientBins<1    % Just in case
    NoOrientBins=1;
end

NoOctaves       = log2(sqrt(2)*(m/2)); % the range we will work with going from 1 c/image to m*sqrt(2) c/image
ScaleMask        = zeros(m,n,NoScaleBins,'uint8');      % Will stores the masks for the two types of bin
ThetaMask        = zeros(m,n,NoOrientBins,'uint8');

low_scale=2.^((([1:NoScaleBins]-1.0)./NoScaleBins) .*NoOctaves);    % The lower...
high_scale=2.^((([1:NoScaleBins])./NoScaleBins) .*NoOctaves);         %... and upper limits of the SF bins
for j=1:NoScaleBins
    ScaleMask(:,:,j)=((A>=low_scale(j))&(A<high_scale(j)));   % Define the mask image to do the SF binning
end

ThetaBinWidth = 0.5*(pi/NoOrientBins);   
ThetaBinLoc=linspace(0,pi,NoOrientBins+1); 
ThetaBinLoc=ThetaBinLoc(1:end-1);                   % Space theta bins evenly
for j=1:NoOrientBins    % Build masks in the same way
    % Key thing is the DirDiff function here which takes into account wrapping
    ThetaMask(:,:,j)=(DirDiff(B,ThetaBinLoc(j))<ThetaBinWidth)|(DirDiff(B+pi,ThetaBinLoc(j))<ThetaBinWidth);
end

% This bit computes the histogram
AmpHist=zeros(NoScaleBins,NoOrientBins);
for j=1:NoScaleBins   % Loop on the two types of bin
    for k=1:NoOrientBins
        SampMask=double(ScaleMask(:,:,j).*ThetaMask(:,:,k)); % The mask is just theproduct of the two types of bin
        SampSize=sum(All(SampMask));                                    % How many pixels in each mask?
        if SampSize>0                                                                 % If greater than zero...
            AmpHist(j,k)=sum(All(SampMask.*f1))./SampSize;      % ...then we can compute the summed amplitude in that region
        else
            AmpHist(j,k)=0;                                                            % otherwise record zero.
        end
    end
end

% This bit plots some functions and computes slope of the amplitude spectrum
if graphics          
    % First plot amplitude as a function of orientation
    OrHist=sum(AmpHist,1);   
    OrHist=[OrHist OrHist OrHist(1)]; % Allows for wrapping (in a polar plot)
    subplot(1,2,1); polar([ThetaBinLoc pi+ThetaBinLoc ThetaBinLoc(1)],OrHist,'bd-'); 
    xlabel('Orientation (deg.)');ylabel('Amplitude');  title('Amplitude as a function of orientation'); 

    % Now plot amplitude as a function of SF
    Scales=2.^((((0.5+[1:NoScaleBins])-1.0)./NoScaleBins) .*NoOctaves);
    AmpHist2=sum(AmpHist,2)';
    goodInd=find((~isnan(AmpHist2))&(AmpHist2>0));   % We're only going to fit powers that are >0 and numbers
    AmpHist2=AmpHist2(goodInd);                                     % Remove other values...
    [p,S] = polyfit(log(Scales(goodInd)),log(AmpHist2),1); % ... and fit the good ones
    fineScale=(linspace(log(Scales(1)),log(Scales(end)),100));   % Finely spaced SFs for plotting the fit line
    PredAmp=exp(polyval(p,fineScale));                                       % And the predicted amplitude based on fitted line

    % Do the plot
    subplot(1,2,2);     loglog(Scales,sum(AmpHist,2)','bd',exp(fineScale),PredAmp,'b-')
    title('Amplitude as a function of SF'); xlabel('SF (c/image)');ylabel('Amplitude');
    legend(sprintf('Slope of amplitude spectrum is %3.3f ',p(1)));
end