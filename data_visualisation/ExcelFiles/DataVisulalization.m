%% Script used to visualize the grid scan for the automatic alignment of 
% the optical alignment stage. 

%% June 9, 2019 Maaike Benedictus

% clear all;
% close all;

filename = 'C:\Users\Jarno\Dropbox\nano\APT_Piezo-master\data_visualisation\ExcelFiles\2019-08-29-10,54,04-UTC-Grindscan.csv'; % filename measured data
filename_figure = '3d plot of scan.png'; % filename for saving the figure
path = "C:\Users\Jarno\Dropbox\nano\APT_Piezo-master\data_visualisation\ExcelFiles\test"; % path for saving files

data = readmatrix(filename);

x = -5:0.01:5;
y = (-5:0.01:5)';
z = exp(-4.*(x.^2+y.^2)) + 1./4.* exp(-6.*(sqrt(x.^2+y.^2) - 1.5).^2); 

fig = figure();
% imagesc(data);

% axis are from 30 till 0 instead of 0 till 30, so they are flipped
surf(z, 'edgecolor', 'none')
colormap(jet)    % change color map
xlabel('y (\mum)');
ylabel('z (\mum)');
title('Grid scan test intensity (W)');
colorbar;

saveas(fig, fullfile(path, filename_figure));
