from manim import *
import numpy as np

# --- CONFIGURATION ---
GRID_SIZE = 40      # Increased to cover the screen
PEG_SPACING = 0.6   # Distance between squares (Manim unit)

# --- WAVE SETTINGS ---
WAVE_AMPLITUDE = 0.5 # Height of the wave (vertical displacement)
WAVE_FREQUENCY = 0.5 # Spatial frequency (higher = tighter waves, lower = wider waves)

# --- ANIMATION LOOP CONTROL ---
LOOP_DURATION = 8.0 # Duration of the video in seconds (One perfect loop)
WAVE_SPEED = (2 * np.pi) / LOOP_DURATION # Auto-calculated speed for perfect loop

# Set resolution
config.pixel_width = 512
config.pixel_height = 256
config.frame_height = 8.0

# --- COLORS (Altitude Palette) ---
COLOR_BACKGROUND = "#FFFFFF"
COLOR_BASE = "#D3D3D3"    # Light Grey
COLOR_LOW = "#0000FF"     # Blue
COLOR_MID = "#FFFF00"     # Yellow
COLOR_HIGH = "#FF0000"    # Red

class IsometricCyberGrid(ThreeDScene):
    """
    Creates a continuously animated isometric grid of shifting blocks, 
    driven by a procedural sine wave.
    """
    def construct(self):
        # 1. SCENE SETUP
        
        # Set the dark cyberpunk background
        self.camera.background_color = COLOR_BACKGROUND
        
        # Set the camera for an isometric view (floor view)
        # phi=60 degrees from Z-axis (30 degrees elevation)
        # theta=-45 degrees (diagonal view)
        self.set_camera_orientation(phi=60 * DEGREES, theta=-60 * DEGREES, gamma=0, zoom=1.4)
        
        # Add a subtle light source (optional but adds depth)
        self.add_fixed_orientation_mobjects(self.get_light(ORIGIN))
        
        # 2. CREATE THE GRID (Mobjects)
        
        # Use a VGroup to hold all the peg/box Mobjects
        grid_group = VGroup()
        
        # Calculate the starting offset to center the grid on the screen
        start_x = -GRID_SIZE * PEG_SPACING / 2
        start_y = -GRID_SIZE * PEG_SPACING / 2 # Now in Y (Floor)

        # Create the grid of squares (pegs)
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                # Pegs are simple 3D Cubes for this purpose
                peg = Cube(side_length=PEG_SPACING, fill_opacity=1.0, stroke_width=3.0, stroke_opacity=1.0, stroke_color=BLACK)
                
                # Initial position based on grid index (XY plane)
                initial_pos = [start_x + i * PEG_SPACING, start_y + j * PEG_SPACING, 0]
                peg.move_to(initial_pos)
                
                # Store the grid indices (i, j) on the mobject for the updater function
                peg.grid_i = i
                peg.grid_j = j
                
                grid_group.add(peg)

        self.add(grid_group)
        
        # 3. IMPLEMENT PROCEDURAL ANIMATION (The Updater)
        
        def wave_updater(mobject, dt):
            """
            Custom function that runs every frame to update the position and color 
            of each peg based on time and its grid position.
            """
            t = self.renderer.time * WAVE_SPEED # Time passed since the scene started
            
            # Iterate through all the pegs in the group
            for peg in mobject:
                i, j = peg.grid_i, peg.grid_j
                
                # Calculate distance from the center (for a circular/radial wave)
                center = GRID_SIZE / 2
                distance = np.sqrt((i - center)**2 + (j - center)**2) * WAVE_FREQUENCY
                
                # Calculate the new vertical height (Z) using the sine wave
                height_factor = np.sin(distance + t)
                new_z = height_factor * WAVE_AMPLITUDE
                
                # Get the current position and update only the Z component (vertical)
                current_pos = peg.get_center()
                peg.move_to([current_pos[0], current_pos[1], new_z])
                
                # --- Dynamic Coloring based on Altitude ---
                
                # Normalize height to 0-1 range
                val = (height_factor + 1) / 2
                
                # Multi-stage gradient: Grey -> Blue -> Yellow -> Red
                if val < 0.33:
                    # Grey to Blue
                    alpha = val / 0.33
                    c1 = ManimColor(COLOR_BASE)
                    c2 = ManimColor(COLOR_LOW)
                    face_color = interpolate_color(c1, c2, alpha)
                elif val < 0.66:
                    # Blue to Yellow
                    alpha = (val - 0.33) / 0.33
                    c1 = ManimColor(COLOR_LOW)
                    c2 = ManimColor(COLOR_MID)
                    face_color = interpolate_color(c1, c2, alpha)
                else:
                    # Yellow to Red
                    alpha = (val - 0.66) / 0.34
                    c1 = ManimColor(COLOR_MID)
                    c2 = ManimColor(COLOR_HIGH)
                    face_color = interpolate_color(c1, c2, alpha)
                
                # Darken the sides slightly for 3D effect
                side_color = interpolate_color(face_color, ManimColor(BLACK), 0.2)
                
                # Color the top face (Face 4) with the main color
                peg[4].set_color(face_color)
                
                # Color the sides with the shaded color
                for k in [0, 1, 2, 3]:
                    peg[k].set_color(side_color)

        # Apply the updater to the entire group
        grid_group.add_updater(wave_updater)
        
        # Run the scene for the configured loop duration
        self.wait(LOOP_DURATION) 

    def get_light(self, position):
        """Helper to create a simple light source mobject."""
        return Sphere(radius=0.1, color=WHITE, fill_opacity=0.8).move_to(position).set_shade_in_3d(False)
