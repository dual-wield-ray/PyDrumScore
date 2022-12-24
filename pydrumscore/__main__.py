"""
Calls the exporter when running 'pydrumscore' from the command line with 'python -m pydrumscore'
"""
from pydrumscore import export
from pydrumscore import export_musicxml

if __name__ == "__main__":
    export_musicxml.main()
