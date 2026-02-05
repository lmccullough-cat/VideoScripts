#!/usr/bin/env python3
"""
Simple PTS jump analyzer - shows specific PTS values where jumps occurred
"""

import re
import sys

def main():
    print("=== PTS Jump Analysis ===\n")
    
    # Get file path from command line argument
    if len(sys.argv) < 2:
        print("Usage: python pts_jump_analyzer.py <file_path>")
        print("Example: python pts_jump_analyzer.py C:\\path\\to\\file.txt")
        return
    
    file_path = sys.argv[1]
    
    print("Loading file:", file_path)
    # Read the file content
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"File loaded successfully!")
    except Exception as e:
        print(f"Error reading file: {e}")
        return
    
    # Extract PTS values from video frames only
    # Split content into frames
    frames = content.split('[FRAME]')
    
    pts_values = []
    for frame in frames:
        if not frame.strip():
            continue
        
        # Check if this is a video frame
        if 'media_type=video' in frame:
            # Extract PTS value from this frame
            pts_match = re.search(r'pts=(\d+)', frame)
            if pts_match:
                pts_values.append(int(pts_match.group(1)))
    
    print(f"Found {len(pts_values)} video PTS values")
    
    # Calculate deltas and find jumps
    if len(pts_values) > 1:
        print("\nAnalyzing PTS deltas for jumps...")
        
        # Calculate all deltas
        deltas = []
        for i in range(1, len(pts_values)):
            delta = pts_values[i] - pts_values[i-1]
            deltas.append(delta)
        
        # Find median and standard deviation
        deltas.sort()
        median_delta = deltas[len(deltas)//2]
        
        # Calculate mean and std dev
        mean_delta = sum(deltas) / len(deltas)
        variance = sum((d - mean_delta)**2 for d in deltas) / len(deltas)
        std_delta = variance ** 0.5
        
        print(f"Median delta: {median_delta} PTS units ({median_delta/90:.2f} ms)")
        print(f"Mean delta: {mean_delta:.2f} PTS units ({mean_delta/90:.2f} ms)")
        print(f"Standard deviation: {std_delta:.2f} PTS units")
        
        # Find anomalies (> 2 standard deviations from mean)
        threshold = mean_delta + (2 * std_delta)
        print(f"Anomaly threshold: {threshold:.2f} PTS units ({threshold/90:.2f} ms)")
        
        print("\n=== PTS VALUES WHERE JUMPS OCCURRED ===")
        anomaly_count = 0
        
        for i in range(1, len(pts_values)):
            delta = pts_values[i] - pts_values[i-1]
            
            if abs(delta - mean_delta) > (2 * std_delta):
                anomaly_count += 1
                prev_pts = pts_values[i-1]
                curr_pts = pts_values[i]
                
                print(f"\nJump #{anomaly_count} at frame {i}:")
                print(f"  Previous PTS: {prev_pts}")
                print(f"  Current PTS:  {curr_pts}")
                print(f"  Delta: {delta} PTS units ({delta/90:.2f} ms)")
                print(f"  Expected: ~{median_delta} PTS units ({median_delta/90:.2f} ms)")
                print(f"  Jump size: {delta - median_delta} PTS units ({(delta - median_delta)/90:.2f} ms) larger than expected")
                print(f"  Estimated FPS: {90000/delta:.2f}")
                
                # Time position in video
                time_seconds = prev_pts / 90000
                print(f"  Time position: {time_seconds:.2f} seconds ({time_seconds//60:.0f}m {time_seconds%60:.1f}s)")
        
        print(f"\nTotal anomalies found: {anomaly_count}")
        
        # Only show largest jumps if there were anomalies detected
        if anomaly_count > 0:
            # Also show some context around large jumps
            print("\n=== LARGEST JUMPS WITH CONTEXT ===")
            
            # Find the largest deltas (skip jumps less than 1ms = 90 PTS units)
            delta_info = []
            for i in range(1, len(pts_values)):
                delta = pts_values[i] - pts_values[i-1]
                if delta >= 90:  # Skip jumps less than 1ms
                    delta_info.append((i, delta, pts_values[i-1], pts_values[i]))
            
            # Sort by delta size and show top 3
            delta_info.sort(key=lambda x: x[1], reverse=True)
            
            for rank, (frame_idx, delta, prev_pts, curr_pts) in enumerate(delta_info[:3], 1):
                print(f"\n#{rank} Largest jump at frame {frame_idx}:")
                print(f"  Previous PTS: {prev_pts}")
                print(f"  Current PTS:  {curr_pts}")
                print(f"  Delta: {delta} PTS units ({delta/90:.2f} ms)")
                
                # Show a few frames before and after for context
                start_idx = max(0, frame_idx - 3)
                end_idx = min(len(pts_values), frame_idx + 4)
                
                print("  Context (frame: PTS -> delta):")
                for j in range(start_idx, end_idx):
                    if j == 0:
                        print(f"    Frame {j}: PTS {pts_values[j]}")
                    else:
                        frame_delta = pts_values[j] - pts_values[j-1]
                        marker = " <-- JUMP" if j == frame_idx else ""
                        print(f"    Frame {j}: PTS {pts_values[j]} -> Δ{frame_delta}{marker}")

if __name__ == "__main__":
    main()
