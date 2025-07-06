import os
import argparse
import pandas as pd
from pydub import AudioSegment

# Adjustable thresholds in milliseconds
SHORT_THRESHOLD = 1000
LONG_THRESHOLD = 3000

def load_dummy_turns():
    # Replace this with your real turn segmentation parser
    return pd.DataFrame({
        "start_ms": [0, 5000, 10000, 18000],
        "end_ms": [4000, 8000, 16000, 24000],
        "speaker": ["A", "B", "A", "C"]
    })

def split_audio(meeting_id, audio_path, output_root):
    output_short = os.path.join(output_root, meeting_id, "segments_short")
    output_long = os.path.join(output_root, meeting_id, "segments_long")
    os.makedirs(output_short, exist_ok=True)
    os.makedirs(output_long, exist_ok=True)

    try:
        audio = AudioSegment.from_wav(audio_path)
        turns = load_dummy_turns()  # Replace with real segmentation
        segment_log = []

        for i, row in turns.iterrows():
            start_ms, end_ms = int(row.start_ms), int(row.end_ms)
            duration = end_ms - start_ms
            segment = audio[start_ms:end_ms]

            if duration < SHORT_THRESHOLD:
                category = "short"
                out_path = os.path.join(output_short, f"{meeting_id}_turn{i}.wav")
            elif duration > LONG_THRESHOLD:
                category = "long"
                out_path = os.path.join(output_long, f"{meeting_id}_turn{i}.wav")
            else:
                continue  # Skip medium turns

            segment.export(out_path, format="wav")
            segment_log.append((meeting_id, i, category, start_ms, end_ms, out_path))

        return segment_log

    except FileNotFoundError:
        print(f"Audio file not found: {audio_path}")
        return []

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus_root", type=str, required=True, help="Path to amicorpus root directory")
    parser.add_argument("--meetings", nargs="+", required=True, help="Meeting IDs to process, e.g. ES2016a ES2016b")
    parser.add_argument("--audio_type", type=str, default="HeadsetMix", help="Type of audio to load: HeadsetMix or LapelMix")
    args = parser.parse_args()

    logs = []
    for meeting_id in args.meetings:
        audio_path = os.path.join(args.corpus_root, meeting_id, "audio", f"{meeting_id}.{args.audio_type}.wav")
        logs.extend(split_audio(meeting_id, audio_path, args.corpus_root))

    # Save metadata log
    if logs:
        df = pd.DataFrame(logs, columns=["meeting", "turn_idx", "type", "start_ms", "end_ms", "path"])
        df.to_csv(os.path.join(args.corpus_root, "segment_log.csv"), index=False)
        print(f"Segment log saved to segment_log.csv with {len(df)} entries.")
    else:
        print("No segments were created.")

if __name__ == "__main__":
    main()
