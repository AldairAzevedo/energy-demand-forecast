function D=sqdist(X,Y)
D = repmat(sum(X.^2,1)',1,size(Y,2)) + repmat(sum(Y.^2,1),size(X,2),1) - 2*X'*Y;

  