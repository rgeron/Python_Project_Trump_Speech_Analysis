import pandas as pd
from pathlib import Path

class OtherCandidatesCorpus:
    def __init__(self, data_dir="data", transcription_file="other_transcriptions.parquet"):
        """
        Initialize the OtherCandidatesCorpus.
        
        Args:
            data_dir (str): Directory containing the parquet files.
            transcription_file (str): Name of the transcription file to load.
        """
        self.data_dir = Path(data_dir)
        self.transcriptions_path = self.data_dir / transcription_file
        
        if not self.transcriptions_path.exists():
            raise FileNotFoundError(f"Transcriptions file not found at {self.transcriptions_path}")
            
        self.transcriptions = pd.read_parquet(self.transcriptions_path)
        
    def get_candidate(self, candidate_name):
        """
        Filter speeches by candidate name.
        
        Args:
            candidate_name (str): The name of the candidate (e.g., "Kamala Harris", "Joe Biden").
            
        Returns:
            OtherCandidatesCorpus: A new instance with filtered data.
        """
        filtered_transcriptions = self.transcriptions[
            self.transcriptions['person_name'] == candidate_name
        ].copy()
        
        if filtered_transcriptions.empty:
            print(f"Warning: No speeches found for candidate '{candidate_name}'")
            
        return self._create_filtered_corpus(filtered_transcriptions)

    def get_kamala(self):
        """
        Filter for speeches by Kamala Harris.
        """
        return self.get_candidate("Kamala Harris")

    def get_biden(self):
        """
        Filter for speeches by Joe Biden.
        """
        return self.get_candidate("Joe Biden")
        
    def _create_filtered_corpus(self, filtered_transcriptions):
        """
        Helper to create a new OtherCandidatesCorpus instance from filtered transcriptions.
        """
        new_corpus = OtherCandidatesCorpus.__new__(OtherCandidatesCorpus)
        new_corpus.data_dir = self.data_dir
        new_corpus.transcriptions_path = self.transcriptions_path
        new_corpus.transcriptions = filtered_transcriptions
        return new_corpus

    def get_full_speeches(self, text_columns=None):
        """
        Aggregate transcriptions to get the full text for each speech.
        
        Args:
            text_columns (list or str, optional): Column(s) to aggregate. 
                                                  If None, defaults to ['text', 'cleaned_transcription'].

        Returns:
            pd.DataFrame: A DataFrame with speech metadata and full text.
                          Includes placeholder columns to match SpeechCorpus schema.
        """
        if text_columns is None:
            text_columns = ['text', 'cleaned_transcription']
        elif isinstance(text_columns, str):
            text_columns = [text_columns]

        # Ensure requested columns exist
        missing_cols = [col for col in text_columns if col not in self.transcriptions.columns]
        if missing_cols:
            available = self.transcriptions.columns.tolist()
            # If default columns are missing, try to be smart or just complain about what's missing
            # For now, let's just warn/error if explicitly requested or default
            # But 'text' should be there. 'cleaned_transcription' might be there.
            # Let's be safe: restrict to what's available if using defaults?
            # User wants "correct cleaned columns".
            pass # We will create available list next

        # Filter cols to only available ones if using default? 
        # No, strict behavior is better. But let's check what we found in terminal.
        # Other: ['text', 'cleaned_transcription', ...] so we are safe.

        # Group by speech_id and person_name to join text
        # We rely on speech_id being unique per speech
        aggregations = {col: lambda x: ' '.join(x.astype(str)) for col in text_columns}
        
        full_text = self.transcriptions.groupby(['speech_id', 'person_name']).agg(aggregations).reset_index()
        
        # Add compatibility columns
        full_text['date'] = pd.NaT  # No date information available
        full_text['title'] = full_text['person_name'].apply(lambda x: f"Speech: {x}")
        full_text['is_rally'] = False # Default assumption or None
        full_text['location'] = None
        full_text['campaign'] = "Other"
        full_text['categories'] = None
        
        # Alias person_name to candidate for clarity
        full_text['candidate'] = full_text['person_name']

        return full_text

    def __repr__(self):
        return f"<OtherCandidatesCorpus: {self.transcriptions['speech_id'].nunique()} speeches>"
