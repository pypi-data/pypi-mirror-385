from ...colors import foreground as fg
from ...colors import background as bg
from ..log.loger import get_logger

logger = get_logger()

RESET = fg.RESET


def prep_doc(action="print"):
    doc = f"""\n\
{fg.DWHITE_FG}Example Usage:{RESET}
    {fg.LWHITE_FG}File Splitting{RESET}:
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} file.mp3 {fg.CYAN_FG}--split --size{RESET} 1mb  {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Using mb{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} file.mp3 {fg.CYAN_FG}--split --size{RESET} 100kb  {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # using kilobytes{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} file.mp3 {fg.CYAN_FG}--split --duration{RESET} 1min {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Split into 1 minute chunks{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} file.mp3 {fg.CYAN_FG}--split --duration{RESET} 1min {fg.CYAN_FG}--count{RESET} 4 {fg.CYAN_FG}--strict{RESET} {fg.CYAN_FG}-O{RESET} splits{RESET}
    {fg.LWHITE_FG}Trimming{bg.RESET}{RESET}:
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} file.mp3 {fg.CYAN_FG}--trim{RESET} {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Trims from 0 to end{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} fime.mp3 {fg.CYAN_FG}--trim --trim_start{RESET} 10sec {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Discards the first 10 seconds{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} fime.mp3 {fg.CYAN_FG}--trim --trim_end{RESET} 1min {fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Discards the last 1 minutes{RESET}
        {fg.GREEN_FG}slicer{fg.YELLOW_FG} fime.mp3 {fg.CYAN_FG}--trim --trim_start{RESET} 10sec {fg.CYAN_FG}--trim_end{RESET} 30sec {fg.DWHITE_FG}{fg.DWHITE_FG}⤗{RESET}{fg.FWHITE_FG} # Discards the first 10 and last seconds respectively{RESET}
        """
    if action == "print":
        print(doc)
    else:
        return doc
