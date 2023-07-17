% MakeMesh
function [X,Y,d,a]=MakeMesh(m,n)
if ~exist('n')
    n=m;
end
[X,Y]=meshgrid([-n/2:n/2-1],[-m/2:m/2-1]);
d=sqrt(X.^2+Y.^2);
t1=(d==0);
a=atan2(Y,X);