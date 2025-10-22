from viktor.external.python import PythonAnalysis

__all__ = ['ETABSAnalysis']

class ETABSAnalysis(PythonAnalysis):
    ''' ::version(14.17.0)

    ETABSAnalysis can be used to evaluate an ETABS-python script on third-party infrastructure. The script is expected
    to be blocking, i.e. if the script is invoked from command prompt, it should wait until the executable is
    finished. The default behaviour, is that the python script is defined within the app and send to the worker to be
    executed on third-party infrastructure. If desired (due to security considerations) the worker can be configured to
    only run local scripts. These scripts must be defined the in worker configuration file and can be selected through
    the `script_key`.

    Usage:

    .. code-block:: python

        script = vkt.File.from_path(Path(__file__).parent / "run_etabs.py")
        files = [
            (\'input1.txt\', file1),
        ]
        analysis = ETABSAnalysis(script=script, files=files, output_filenames=["output.txt"])
        analysis.execute(timeout=60)
        output_file = analysis.get_output_file("output.txt")

    Exceptions which can be raised during calculation:

        - :class:`viktor.errors.LicenseError`: no license available
        - :class:`viktor.errors.ExecutionError`: generic error. Error message provides more information
    '''
