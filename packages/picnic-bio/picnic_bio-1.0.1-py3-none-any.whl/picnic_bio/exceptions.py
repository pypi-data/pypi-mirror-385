"""Custom exceptions for Picnic."""


class NoGoAnnotationFoundError(Exception):
    """Exception for cases when no GO annotation could be fetched from UniProt."""

    def __init__(self, uniprot_id):
        self.uniprot_id = uniprot_id
        self.message = (
            f"Could not find any GO annotations for protein {self.uniprot_id}! Therefore it is not "
            f"possible to calculate Picnic GO. Please use the default Picnic model (set boolean "
            f"flag <is_go> to False) for the score calculation."
        )
        super(Exception, self).__init__(self.message)


class CouldNotDownloadAlphaFoldModelError(Exception):
    """Exception for cases when AlphaFold cannot be downloaded from API."""

    def __init__(self, uniprot_id, err_msg):
        self.uniprot_id = uniprot_id
        self.err_msg = err_msg
        self.message = f"Could NOT download AlphaFold model file for UniProt Id: {self.uniprot_id}! Received the following server message: {self.err_msg}."
        super(Exception, self).__init__(self.message)


class CouldNotDownloadFASTAFileError(Exception):
    """Exception for cases when FASTA file cannot be downloaded from API."""

    def __init__(self, uniprot_id, err_msg):
        self.uniprot_id = uniprot_id
        self.err_msg = err_msg
        self.message = f"Could NOT download FASTA file for UniProt Id: {self.uniprot_id}! Received the following server message: {self.err_msg}."
        super(Exception, self).__init__(self.message)


class CouldNotParseFASTAFileError(Exception):
    """Exception for cases when FASTA file cannot be parsed."""

    def __init__(self, fasta_file_path):
        self.fasta_file_path = fasta_file_path
        self.message = f"Could NOT parse FASTA file: {self.fasta_file_path}!"
        super(Exception, self).__init__(self.message)


class InvalidUniProtIdProvidedError(Exception):
    """Exception for cases when an invalid UniProt Id has been provided."""

    def __init__(self, uniprot_id):
        self.uniprot_id = uniprot_id
        self.message = f"Invalid UniProt Id provided: {uniprot_id}! Please make sure that the provided UniProt Id is not empty | None."
        super(Exception, self).__init__(self.message)


class NoAlphaFoldModelProvidedError(Exception):
    """Exception for cases when NO AlphaFold model provide in manual mode."""

    def __init__(self, model_file_folder):
        self.model_file_folder = model_file_folder
        self.message = f"No AlphaFold model file found in the specified model file folder: {self.model_file_folder}."
        super(Exception, self).__init__(self.message)
