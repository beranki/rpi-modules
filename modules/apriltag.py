import numpy as np
import cv2
import matplotlib.pyplot as plt
import os

#basically fixes the intrinsic parameters and is the class that returns the 3D stuff
class AprilTag():

    def __init__(self):
        pass

    def calibrate_camera(self, images_directory, pattern_size, square_size):
        # Prepare object points based on the number of squares and their size
        objp = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[0:pattern_size[0], 0:pattern_size[1]].T.reshape(-1, 2) * square_size

        # Arrays to store object points and image points from all images
        objpoints = []  # 3D points in real-world space
        imgpoints = []  # 2D points in the image plane

        # Get the list of image files in the directory
        image_files = [f for f in os.listdir(images_directory) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        for fname in image_files:
            img_path = os.path.join(images_directory, fname)
            img = cv2.imread(img_path)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Find the chessboard corners
            ret, corners = cv2.findChessboardCorners(gray, pattern_size, None)

            # If found, add object points and image points
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)

                # Draw and display the corners
                img = cv2.drawChessboardCorners(img, pattern_size, corners, ret)
                cv2.imshow('Chessboard Corners', img)
                cv2.waitKey(500)  # Adjust the waiting time as needed

        cv2.destroyAllWindows()

        # Calibrate the camera
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
            objpoints, imgpoints, gray.shape[::-1], None, None
        )
        if ret:
            print('Calibration completed')
        else:
            print('Calibration failed')

        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs

    def estimate_pose_single_marker(self, corners, marker_size, camera_matrix, dist_coeffs):
        try:
            # Ensure corners is a NumPy array
            corners = np.array(corners)

            # Define the 3D coordinates of the marker corners in the marker coordinate system
            marker_points_3d = np.array([[0, 0, 0], [marker_size, 0, 0], [marker_size, marker_size, 0], [0, marker_size, 0]], dtype=np.float32)

            # Reshape the corners to a flat array
            image_points_2d = corners.reshape(-1, 2)

            # Convert image points to float32
            image_points_2d = np.float32(image_points_2d)

            # Solve PnP problem to estimate pose
            _, rvec, tvec = cv2.solvePnP(marker_points_3d, image_points_2d, camera_matrix, dist_coeffs)

            return rvec, tvec

        except Exception as e:
            print(f"An error occurred: {e}")
            return None, None


    def draw_axis_on_image(self, image, camera_matrix, dist_coeffs, rvec, tvec, size=0.1):
        try:
            # Define axis length
            length = size

            # 3D axis points in the marker coordinate system
            axis_points_3d = np.float32([[0, 0, 0], [length, 0, 0], [0, length, 0], [0, 0, -length]])

            # Project 3D points to image plane
            axis_points_2d, _ = cv2.projectPoints(axis_points_3d, rvec, tvec, camera_matrix, dist_coeffs)

            # Convert to integer
            axis_points_2d = np.int32(axis_points_2d).reshape(-1, 2)

            # Draw axis lines directly on the image
            cv2.line(image, tuple(axis_points_2d[0]), tuple(axis_points_2d[1]), (0, 0, 255), 2)  # X-axis (red)
            cv2.line(image, tuple(axis_points_2d[0]), tuple(axis_points_2d[2]), (0, 255, 0), 2)  # Y-axis (green)
            cv2.line(image, tuple(axis_points_2d[0]), tuple(axis_points_2d[3]), (255, 0, 0), 2)  # Z-axis (blue)
            return image

        except Exception as e:
            print(f"An error occurred: {e}")
            return None
        
    def estimate_3d_pose(self, image, frame_ann):
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Create an AprilTag detector
            aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_APRILTAG_16h5)
            parameters = cv2.aruco.DetectorParameters()
            parameters.adaptiveThreshWinSizeMin = 3
            parameters.adaptiveThreshWinSizeMax = 23
            parameters.adaptiveThreshWinSizeStep = 10
            parameters.adaptiveThreshConstant = 7
            detector = cv2.aruco.ArucoDetector(aruco_dict, detectorParams=parameters)
            # Detect AprilTags in the image
            corners, ids, rejected_img_points = detector.detectMarkers(gray)
            pose_data = {}
            num_tags = len(ids) if ids is not None else 0
            #print(str(num_tags) + ' AprilTags detected')
            if num_tags != 0:
                # Draw the detected markers on the image
                cv2.aruco.drawDetectedMarkers(image, corners, ids)

                # Estimate the pose of each detected marker
                for i in range(len(ids)):
                    # Estimate the pose
                    rvec, tvec= self.estimate_pose_single_marker(corners[i], 0.05, self.camera_matrix, self.dist_coeffs)
                    pose_data[ids[i][0]] = (tvec, rvec)
                    # Draw the 3D pose axis on the image
                    self.draw_axis_on_image(frame_ann, self.camera_matrix, self.dist_coeffs, rvec, tvec, 0.1)

                # Display the result
                cv2.imshow('AprilTag Pose Estimation', image)
            else:
                #print("No AprilTags detected in the image.")
                pass
            return pose_data
            



