# We will test the main method here

from main import main

def test_main(config, sample_pdf_file):
    '''
    Test main method
    '''

    main(config = config, pdf_file=sample_pdf_file)