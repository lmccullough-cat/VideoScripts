import sys
import traceback
import struct
from pathlib import Path

def parse_stss(data):
    """Parse Sync Sample Table (stss) - returns list of I-frame sample numbers"""
    version = data[0]
    flags = int.from_bytes(data[1:4], byteorder='big')
    entry_count = int.from_bytes(data[4:8], byteorder='big')
    
    entries = []
    for i in range(entry_count):
        offset = 8 + (i * 4)
        sample_number = int.from_bytes(data[offset:offset+4], byteorder='big')
        entries.append(sample_number)
    
    return entries

def parse_stco(data):
    """Parse Chunk Offset Table (stco) - returns list of chunk offsets"""
    version = data[0]
    flags = int.from_bytes(data[1:4], byteorder='big')
    entry_count = int.from_bytes(data[4:8], byteorder='big')
    
    offsets = []
    for i in range(entry_count):
        offset = 8 + (i * 4)
        chunk_offset = int.from_bytes(data[offset:offset+4], byteorder='big')
        offsets.append(chunk_offset)
    
    return offsets

def parse_co64(data):
    """Parse 64-bit Chunk Offset Table (co64)"""
    version = data[0]
    flags = int.from_bytes(data[1:4], byteorder='big')
    entry_count = int.from_bytes(data[4:8], byteorder='big')
    
    offsets = []
    for i in range(entry_count):
        offset = 8 + (i * 8)
        chunk_offset = int.from_bytes(data[offset:offset+8], byteorder='big')
        offsets.append(chunk_offset)
    
    return offsets

def parse_stsz(data):
    """Parse Sample Size Table (stsz) - returns list of sample sizes"""
    version = data[0]
    flags = int.from_bytes(data[1:4], byteorder='big')
    sample_size = int.from_bytes(data[4:8], byteorder='big')
    sample_count = int.from_bytes(data[8:12], byteorder='big')
    
    if sample_size != 0:
        # All samples have the same size
        return [sample_size] * sample_count
    else:
        # Each sample has its own size
        sizes = []
        for i in range(sample_count):
            offset = 12 + (i * 4)
            size = int.from_bytes(data[offset:offset+4], byteorder='big')
            sizes.append(size)
        return sizes

def parse_stsc(data):
    """Parse Sample to Chunk Table (stsc) - returns list of (first_chunk, samples_per_chunk, sample_description_index)"""
    version = data[0]
    flags = int.from_bytes(data[1:4], byteorder='big')
    entry_count = int.from_bytes(data[4:8], byteorder='big')
    
    entries = []
    for i in range(entry_count):
        offset = 8 + (i * 12)
        first_chunk = int.from_bytes(data[offset:offset+4], byteorder='big')
        samples_per_chunk = int.from_bytes(data[offset+4:offset+8], byteorder='big')
        sample_description_index = int.from_bytes(data[offset+8:offset+12], byteorder='big')
        entries.append((first_chunk, samples_per_chunk, sample_description_index))
    
    return entries

def extract_iframe_offsets(mp4_path):
    offsets = []
    all_samples = []  # Track all sample offsets and sizes for validation
    with open(mp4_path, 'rb') as f:
        data = f.read()
    
    file_size = len(data)

    # Find moov box
    pos = 0
    moov_start = None
    moov_size = None
    
    while pos < len(data):
        if pos + 8 > len(data):
            break
        box_size = int.from_bytes(data[pos:pos+4], byteorder='big')
        box_type = data[pos+4:pos+8]
        
        if box_size == 0:
            box_size = len(data) - pos
        elif box_size == 1:
            box_size = int.from_bytes(data[pos+8:pos+16], byteorder='big')
        
        if box_type == b'moov':
            moov_start = pos
            moov_size = box_size
            break
        
        pos += box_size

    if not moov_start:
        raise ValueError("No 'moov' box found — invalid MP4 file.")

    # Find mdat box for validation
    pos = 0
    mdat_start = None
    mdat_end = None
    
    while pos < len(data):
        if pos + 8 > len(data):
            break
        box_size = int.from_bytes(data[pos:pos+4], byteorder='big')
        box_type = data[pos+4:pos+8]
        
        if box_size == 0:
            box_size = len(data) - pos
        elif box_size == 1:
            box_size = int.from_bytes(data[pos+8:pos+16], byteorder='big')
        
        if box_type == b'mdat':
            mdat_start = pos + 8  # Data starts after the 8-byte header
            mdat_end = pos + box_size
            break
        
        pos += box_size

    # Navigate through moov -> trak -> mdia -> minf -> stbl
    moov_data = data[moov_start:moov_start+moov_size]
    
    # Find all trak boxes
    pos = 8  # Skip moov header
    while pos < len(moov_data):
        if pos + 8 > len(moov_data):
            break
        box_size = int.from_bytes(moov_data[pos:pos+4], byteorder='big')
        box_type = moov_data[pos+4:pos+8]
        
        if box_size == 0:
            box_size = len(moov_data) - pos
        elif box_size == 1:
            box_size = int.from_bytes(moov_data[pos+8:pos+16], byteorder='big')
        
        if box_type == b'trak':
            # Found a track, navigate to stbl
            trak_data = moov_data[pos:pos+box_size]
            
            # Find mdia
            trak_pos = 8
            while trak_pos < len(trak_data):
                if trak_pos + 8 > len(trak_data):
                    break
                inner_size = int.from_bytes(trak_data[trak_pos:trak_pos+4], byteorder='big')
                inner_type = trak_data[trak_pos+4:trak_pos+8]
                
                if inner_type == b'mdia':
                    mdia_data = trak_data[trak_pos:trak_pos+inner_size]
                    
                    # Find minf
                    mdia_pos = 8
                    while mdia_pos < len(mdia_data):
                        if mdia_pos + 8 > len(mdia_data):
                            break
                        minf_size = int.from_bytes(mdia_data[mdia_pos:mdia_pos+4], byteorder='big')
                        minf_type = mdia_data[mdia_pos+4:mdia_pos+8]
                        
                        if minf_type == b'minf':
                            minf_data = mdia_data[mdia_pos:mdia_pos+minf_size]
                            
                            # Find stbl
                            minf_pos = 8
                            while minf_pos < len(minf_data):
                                if minf_pos + 8 > len(minf_data):
                                    break
                                stbl_size = int.from_bytes(minf_data[minf_pos:minf_pos+4], byteorder='big')
                                stbl_type = minf_data[minf_pos+4:minf_pos+8]
                                
                                if stbl_type == b'stbl':
                                    stbl_data = minf_data[minf_pos:minf_pos+stbl_size]
                                    
                                    # Parse stbl children manually
                                    stss_data = None
                                    stco_data = None
                                    co64_data = None
                                    stsz_data = None
                                    stsc_data = None
                                    
                                    stbl_pos = 8
                                    while stbl_pos < len(stbl_data):
                                        if stbl_pos + 8 > len(stbl_data):
                                            break
                                        child_size = int.from_bytes(stbl_data[stbl_pos:stbl_pos+4], byteorder='big')
                                        child_type = stbl_data[stbl_pos+4:stbl_pos+8]
                                        child_data = stbl_data[stbl_pos+8:stbl_pos+child_size]
                                        
                                        if child_type == b'stss':
                                            stss_data = child_data
                                        elif child_type == b'stco':
                                            stco_data = child_data
                                        elif child_type == b'co64':
                                            co64_data = child_data
                                        elif child_type == b'stsz':
                                            stsz_data = child_data
                                        elif child_type == b'stsc':
                                            stsc_data = child_data
                                        
                                        stbl_pos += child_size
                                    
                                    # Process if we have all required boxes
                                    if stss_data and (stco_data or co64_data) and stsz_data and stsc_data:
                                        iframe_samples = set(parse_stss(stss_data))
                                        chunk_offsets = parse_stco(stco_data) if stco_data else parse_co64(co64_data)
                                        sample_sizes = parse_stsz(stsz_data)
                                        stsc_entries = parse_stsc(stsc_data)
                                        
                                        # Build sample-to-chunk map
                                        sample_to_chunk_map = []
                                        for i, entry in enumerate(stsc_entries):
                                            first_chunk = entry[0]
                                            samples_per_chunk = entry[1]
                                            
                                            if i + 1 < len(stsc_entries):
                                                last_chunk = stsc_entries[i + 1][0] - 1
                                            else:
                                                last_chunk = len(chunk_offsets)
                                            
                                            for chunk_num in range(first_chunk, last_chunk + 1):
                                                sample_to_chunk_map.append((chunk_num, samples_per_chunk))
                                        
                                        # Map sample numbers to byte offsets
                                        sample_index = 1
                                        for chunk_num, samples_per_chunk in sample_to_chunk_map:
                                            chunk_offset = chunk_offsets[chunk_num - 1]
                                            sample_offset = chunk_offset
                                            
                                            for _ in range(samples_per_chunk):
                                                if sample_index > len(sample_sizes):
                                                    break
                                                
                                                sample_size = sample_sizes[sample_index - 1]
                                                
                                                # Track all samples for frame count validation
                                                all_samples.append({
                                                    'offset': sample_offset,
                                                    'size': sample_size,
                                                    'is_iframe': sample_index in iframe_samples
                                                })
                                                
                                                if sample_index in iframe_samples:
                                                    offsets.append(sample_offset)
                                                
                                                sample_offset += sample_size
                                                sample_index += 1
                                
                                minf_pos += stbl_size
                        
                        mdia_pos += minf_size
                
                trak_pos += inner_size
        
        pos += box_size

    # Validate offsets
    validated_offsets = []
    invalid_offsets = []
    
    for offset in sorted(set(offsets)):
        is_valid = True
        reason = []
        
        # Check if offset is within file bounds
        if offset >= file_size:
            is_valid = False
            reason.append(f"exceeds file size ({file_size})")
        
        # Check if offset is within mdat box if mdat exists
        if mdat_start is not None and mdat_end is not None:
            if offset < mdat_start or offset >= mdat_end:
                is_valid = False
                reason.append(f"outside mdat box ({mdat_start}-{mdat_end})")
        
        # Check if there's enough data at offset for a valid sample
        if offset + 4 <= file_size:
            # Check for common NAL unit start codes (H.264/H.265)
            # 0x00000001 or 0x000001 are common start codes
            sample_start = data[offset:offset+4]
            if len(sample_start) == 4:
                # Check for 4-byte start code (0x00000001)
                if sample_start == b'\x00\x00\x00\x01':
                    pass  # Valid start code
                # Check for 3-byte start code (0x000001)
                elif sample_start[:3] == b'\x00\x00\x01':
                    pass  # Valid start code
                # For some MP4s, samples may not have start codes (they use length-prefixed NALs)
                # So we'll just warn if no start code is found
        else:
            is_valid = False
            reason.append("insufficient data at offset")
        
        if is_valid:
            validated_offsets.append(offset)
        else:
            invalid_offsets.append((offset, ", ".join(reason)))
    
    # Validate frame count: Check if samples in moov match data in mdat
    frames_in_moov = len(all_samples)
    frames_outside_mdat = 0
    total_size_from_moov = 0
    
    for sample in all_samples:
        total_size_from_moov += sample['size']
        if mdat_start is not None and mdat_end is not None:
            if sample['offset'] < mdat_start or sample['offset'] + sample['size'] > mdat_end:
                frames_outside_mdat += 1
    
    # Calculate actual mdat size
    actual_mdat_size = mdat_end - mdat_start if (mdat_start and mdat_end) else 0
    
    return validated_offsets, invalid_offsets, file_size, mdat_start, mdat_end, frames_in_moov, frames_outside_mdat, total_size_from_moov, actual_mdat_size

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} <video.mp4>")
        sys.exit(1)

    mp4_file = sys.argv[1]
    try:
        validated_offsets, invalid_offsets, file_size, mdat_start, mdat_end, frames_in_moov, frames_outside_mdat, total_size_from_moov, actual_mdat_size = extract_iframe_offsets(mp4_file)
        
        # Print file information
        print(f"File: {mp4_file}")
        print(f"File size: {file_size:,} bytes")
        if mdat_start and mdat_end:
            print(f"Media data (mdat) range: {mdat_start:,} - {mdat_end:,} bytes")
            print(f"Actual mdat size: {actual_mdat_size:,} bytes")
        print()
        
        # Print frame count information
        print(f"Frames in moov atom (index): {frames_in_moov:,}")
        print(f"Total I-frames found: {len(validated_offsets) + len(invalid_offsets)}")
        print(f"Valid I-frames: {len(validated_offsets)}")
        print(f"Invalid I-frames: {len(invalid_offsets)}")
        
        # Check for frame count mismatch
        if frames_outside_mdat > 0:
            print(f"\n[WARNING] Frame count mismatch detected!")
            print(f"  Frames with offsets outside mdat: {frames_outside_mdat}")
        
        # Check if total size from moov matches mdat size
        if actual_mdat_size > 0:
            size_diff = abs(total_size_from_moov - actual_mdat_size)
            size_ratio = (total_size_from_moov / actual_mdat_size * 100) if actual_mdat_size > 0 else 0
            if size_diff > actual_mdat_size * 0.1:  # More than 10% difference
                print(f"\n[WARNING] Significant size mismatch detected!")
                print(f"  Total frame size from moov: {total_size_from_moov:,} bytes")
                print(f"  Actual mdat size: {actual_mdat_size:,} bytes")
                print(f"  Difference: {size_diff:,} bytes ({100 - size_ratio:.1f}% mismatch)")
        
        print()
        
        # Only print invalid offsets
        if invalid_offsets:
            print(f"Invalid I-frame offsets:")
            for offset, reason in invalid_offsets:
                print(f"  {offset}: {reason}")
        else:
            print("All I-frame offsets are valid.")
            
    except Exception as e:
        # Print detailed error info with traceback
        print("\n[ERROR] An exception occurred!")
        print(f"Type: {type(e).__name__}")
        print(f"Message: {e}")
        print("Traceback (most recent call last):")
        traceback.print_exc()
        sys.exit(1)
