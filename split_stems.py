from step1_BPMAnalysis import load_and_analyze_bpm
from step2_KeyAnalysis import detect_key
from step3_GUI import AudioProcessingGUI
from step4_StemSeperation import separate_stems
from step5_DrumSeperation import separate_drums
from step6_OtherSeperation import separate_other

def main():
    print("\n=== Starting Stem Separator ===")
    gui = AudioProcessingGUI()
    gui.run()
    print("=== Process Complete ===\n")

if __name__ == "__main__":
    main()