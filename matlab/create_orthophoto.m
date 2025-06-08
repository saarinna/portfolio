function []=create_orthophoto()
format long g % Display more decimals in the command window for precision

% Read laser scanner data points (X, Y, Z)
laserdata=read_laserdata();

% Read camera parameters: principal point coordinates, camera constant, rotation matrix, and projection center coordinates
[pp_x,pp_y,c,R,X0,Y0,Z0]=read_camera_parameters();

% Extract x and y coordinates from laser data
x_values = laserdata(:, 1);
y_values = laserdata(:, 2);

% Calculate maximum and minimum ground coordinates from laser points
maxValueX = max(x_values);
minValueX = min(x_values);
maxValueY = max(y_values);
minValueY = min(y_values);

% Display max and min values for debugging and understanding data extent
fprintf('Max X:')
disp(maxValueX)
fprintf('Min X:')
disp(minValueX)
fprintf('Max Y:')
disp(maxValueY)
fprintf('Min y:')
disp(minValueY)

% Load the grayscale aerial image to be used for orthophoto generation
image=imread('test_image_gray.tif');
imsize=size(image) %image dimensions (rows, columns) % Get image dimensions [rows, columns]

% Visualize the original image before processing
figure(1)
imshow(image)
title('Original image')

% Define the ground sampling distance (grid size) for orthophoto pixels
grid_size=0.2; %grid size of ortho image

% Calculate how many pixels are needed in x and y to cover the laser data extent
% Implemented by me
pixels_columns = fix((maxValueX - minValueX) / (grid_size))   % The area covered (metric) divided with grid_size
pixels_rows = fix((maxValueY - minValueY) / (grid_size))

% Display the size of the orthophoto grid
% Implemented by me
fprintf('Pixel columns: '); disp(pixels_columns)
fprintf('Pixel rows: '); disp(pixels_rows)

% Initialize the orthophoto image matrix (grayscale) and DEM (height) matrix
orthophoto=zeros(pixels_rows, pixels_columns); 
DEM=zeros(pixels_rows, pixels_columns);

% Define starting ground coordinates corresponding to pixel (1,1). Y axis is flipped in image vs ground coordinates
% Implemented by me
start_x = fix(minValueX)
start_y = fix(maxValueY)
    
% Create a KD-tree for efficient nearest neighbor searching in laser points
tree = KDTreeSearcher(laserdata(:,1:2));

% Loop through each pixel of the orthophoto image grid
for i=1:pixels_rows
   for j= 1:pixels_columns
		% Calculate ground coordinates of the current pixel center
		X=start_x+(j-1)*grid_size;
		Y=start_y-(i-1)*grid_size; % Y decreases with increasing row index

		% Find the 5 closest laser points to current ground coordinate using KD-tree
		[Idx,D] = knnsearch(tree, [X,Y], 'K', 5);
		closest_5 = [D.', laserdata(Idx,:)]; % Store distances and point data'
		
		% Perform inverse distance weighting interpolation to estimate height
		interpolated_height=inverse_distance_weighting_interpolation(X,Y,closest_5);
		
		% Store the interpolated height in the DEM matrix
		DEM(i,j)=interpolated_height;
		
		% Project the 3D ground point (X, Y, height) into the camera image plane
		[x_camera, y_camera]=collinearity_equations(X, Y, interpolated_height,  c, X0, Y0, Z0, R);

		% Convert camera coordinates to image pixel coordinates 
		[row,column]=camera_coordinates2image_coordinates(x_camera, y_camera, pp_x, pp_y);

		% Check if the projected pixel lies inside the image boundaries
		if row>1 && column>1 && row<imsize(1)+1 && column<imsize(2)+1
			% Perform bilinear interpolation of grayscale value from neighboring pixels
			interpolated_color=uint8(bilinear_interpolation(column, row, double(image(floor(row),floor(column))), double(image(floor(row),ceil(column))), double(image(ceil(row),floor(column))), double(image(ceil(row),ceil(column)))));
				
			% Assign the interpolated grayscale value to orthophoto pixel
			orthophoto(i,j)=interpolated_color; %setting interpolated color value to ortho image
		else
			% If outside image, set pixel color to black (0)
			orthophoto(i,j)=0;
   		end
   	end
end

% Display the generated orthophoto
figure(2)
im=imshow(mat2gray(orthophoto)); % Normalize matrix to image intensity range
title('Orthophoto')

end

% Function to read laser scanner data from a text file
% Function given in task instructions
function [laserdata]=read_laserdata()
	laserdata=load('laserdata.txt'); %todo:check if you need path to file
end

% Function to read camera calibration and orientation parameters from file
% Function given in task instructions
function [pp_x,pp_y,c,R, X0,Y0,Z0]=read_camera_parameters()
    f=fopen('camera_orientation_info.txt'); %todo:check if you need a path to file
    line = fgets(f);%skip line
    
    %principle point
    line = fgets(f);
    pp_x = sscanf(line,'%f');
    line = fgets(f);
    pp_y = sscanf(line,'%f');
    
    line = fgets(f);%skip line
    
    %camera constant
    line = fgets(f);
    c = sscanf(line,'%f');
    
    line = fgets(f);%skip line
    line = fgets(f);%skip line
    line = fgets(f);%skip line
    line = fgets(f);%skip line
    
    %projection center
    line = fgets(f);
    X0 = sscanf(line,'%f');
    line = fgets(f);
    Y0 = sscanf(line,'%f');
    line = fgets(f);
    Z0 = sscanf(line,'%f');     
    
    line = fgets(f);%skip line
    
    %rotation matrix
    R=zeros(3,3);
    line = fgets(f);
    R(1,:)=sscanf(line,'%f %f %f'); 
    line = fgets(f);
    R(2,:)=sscanf(line,'%f %f %f');
    line = fgets(f);
    R(3,:)=sscanf(line,'%f %f %f');


    fclose(f);%close file
end

% Inverse Distance Weighting (IDW) interpolation for height
% Implemented by me
function [interpolated_height]=inverse_distance_weighting_interpolation(X,Y,closest_5)
    % closest_5: Nx5 matrix with first column distance and others with X,Y,Z
	w_i = zeros(5,1); % Initialize weights
	u_i = closest_5(:, 4); % Extract height (Z) values
 	  
	% Calculate weights inversely proportional to squared distances
	for i=1:size(closest_5, 1)
    	d = closest_5(i,1);
    	w = 1 / (d.^2);
    	w_i(i) = w;
	end
   
	w_j = sum(w_i); % Sum of weights
    
	u = zeros(5,1); % Initialise u as a 5x1 matrix
    
	% Calculate weighted sum of heights
	for i=1:size(u, 1)
    	u(i) = (w_i(i)*u_i(i))/w_j;
	end
    
	% Final interpolated height is sum of weighted heights
	interpolated_height = sum(u);
end

% Collinearity equations to project ground point into camera image plane
% Implemented by me
function [x_camera, y_camera]=collinearity_equations(X, Y, Z, c, X0, Y0, Z0, R) 
	% The collinearity equations
	x_camera = -c * (R(1,1)*(X-X0) + R(1,2)*(Y-Y0) + R(1,3)*(Z-Z0)) / (R(3,1)*(X-X0) + R(3,2)*(Y-Y0) + R(3,3)*(Z-Z0));
	y_camera = -c * (R(2,1)*(X-X0) + R(2,2)*(Y-Y0) + R(2,3)*(Z-Z0)) / (R(3,1)*(X-X0) + R(3,2)*(Y-Y0) + R(3,3)*(Z-Z0));
end

% Bilinear interpolation of grayscale value in the image
% Implemented by me
function [interpolated_color]=bilinear_interpolation(x_image, y_image, color1, color2, color3, color4)
	% color1 = top-left pixel, color2 = top-right pixel
		%color1 = row,column; color2=row,column+1; color3=row+1,column; color4=row+1,column+1  
    % color3 = bottom-left pixel, color4 = bottom-right pixel
    
	% Find integer pixel coordinates (top-left corner of interpolation square)
	column = floor(x_image);
	row = floor(y_image);
    
	% Compute fractional parts in x and y directions
	delta_x = x_image - column;
	delta_y = y_image - row;

	% Compute bilinear interpolation formula
	interpolated_color = (1 - delta_x)*(1-delta_y)*color1+delta_x*(1-delta_y)*color2+(1-delta_x)*delta_y*color3+delta_x*delta_y*color4;
    
	% Round to nearest integer to get pixel intensity
	interpolated_color = round(interpolated_color);
end