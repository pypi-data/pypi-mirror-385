import re

from dataclasses import dataclass
from enum import Enum
from typing import List

from .constants import UNIX_DOW, UNIX_MONTHS

def is_int(value):
    return isinstance(value, int) and not isinstance(value, bool)


class DataLossCause(Enum):
    """An Enum of possible data loss causes."""

    SECOND_WAS_NOT_ZERO = "second field was not 0"
    DOM_WAS_QUESTIONMARK = "dom field was the special character ?"
    DOM_WAS_L = "dom field was the special character L"
    DOM_CONTAINED_L = "dom field contained the special character L"
    DOM_CONTAINED_W = "dom field contained the special character W"
    DOW_WAS_QUESTIONMARK = "dow field was the special character ?"
    DOW_WAS_L = "dow field was special the character L"
    DOW_CONTAINED_L = "dow field contained the special character L"
    DOW_CONTAINED_HASH = "dow field contained the special character #"
    YEAR_WAS_DEFINED = "optional year field was defined"

    def __str__(self):
        return self.value


@dataclass
class Result:
    """
    A class used to represent a quartz2unix conversion result.

    :param quartz_cron:
        The quartz cron expression that was converted to the unix cron expression.
    :type quartz_cron: str
    :param unix_cron:
        The unix cron expression that was converted from the quartz cron expression.
    :type unix_cron: str
    :param data_loss:
        List of data losses that occurred during the conversion.
    :type data_loss: list[DataLossCause]
    """

    quartz_cron: str
    unix_cron: str
    data_loss: List[DataLossCause]


def convert(quartz_cron: str, settings: dict={"dom_l_replacement": 1}) -> Result:
    """
    Converts a quartz cron expression to a unix cron expression.

    :param quartz_cron:
        A quartz cron expression.
    :type quartz_cron: str
    :param settings:
        A dict that contains the settings keys.
    :type settings: dict
    :param settings.dom_l_replacement:
        The replacement for the special character "L" in the dom field.
        Default value is 1. (First day of the month
        instead of the last day of the month.)
    :type settings.dom_l_replacement: int
    :returns: A cronverter.quartz2unix.Result object
    :rtype: Result
    """

    # validate settings values
    if not is_int(settings["dom_l_replacement"]) or not 1 <= settings["dom_l_replacement"] <= 31:
        raise ValueError(
            f"Invalid value for \"dom_l_replacement\": {settings['dom_l_replacement']}. Expected an integer between 1 and 31 (inclusive)."
        )

    quartz_cron_array = quartz_cron.split(" ")
    data_loss = []

    # second
    ## second - not 0
    if quartz_cron_array[0] != "0":
        data_loss.append(DataLossCause.SECOND_WAS_NOT_ZERO)

    # minute
    minute = quartz_cron_array[1]

    # hour
    hour = quartz_cron_array[2]

    # dom (day of month)
    ## dom - is special character ?
    if quartz_cron_array[3] == "?":
        data_loss.append(DataLossCause.DOM_WAS_QUESTIONMARK)
        quartz_cron_array[3] = "*"
    ## dom - is special character L
    elif quartz_cron_array[3] == "L":
        data_loss.append(DataLossCause.DOM_WAS_L)
        quartz_cron_array[3] = settings["dom_l_replacement"]
    else:
        ## dom - contains special character L
        if "L" in quartz_cron_array[3]:
            data_loss.append(DataLossCause.DOM_CONTAINED_L)
            quartz_cron_array[3].replace("L", str(settings["dom_l_replacement"]))
        ## dom - contains special character W
        if "W" in quartz_cron_array[3]:
            data_loss.append(DataLossCause.DOM_CONTAINED_W)
            quartz_cron_array[3] = quartz_cron_array[3].replace("W", "")
    dom = quartz_cron_array[3]

    # month
    ## month - transform names to numbers
    month = re.sub(
        r"\b(" + "|".join(UNIX_MONTHS.keys()) + r")\b",
        lambda m: UNIX_MONTHS[m.group(1)],
        quartz_cron_array[4]
    )

    # dow (day of week)
    ## dow - is special character ?
    if quartz_cron_array[5] == "?":
        data_loss.append(DataLossCause.DOW_WAS_QUESTIONMARK)
        quartz_cron_array[5] = "*"
    ## dow - is special character L
    elif quartz_cron_array[5] == "L":
        data_loss.append(DataLossCause.DOW_WAS_L)
        quartz_cron_array[5] = "0"
    else:
        ## dow - contains special character L
        if "L" in quartz_cron_array[5]:
            data_loss.append(DataLossCause.DOW_CONTAINED_L)
            quartz_cron_array[5].replace("L", "")
        ## dow - contains special character #
        if "#" in quartz_cron_array[5]:
            data_loss.append(DataLossCause.DOW_CONTAINED_HASH)
            quartz_cron_array[5] = quartz_cron_array[5][:-2]
        ## dow - number offset
        quartz_cron_array[5] = re.sub(
            r"\b[1-7]\b",
            lambda d: str(int(d.group()) - 1),
            quartz_cron_array[5]
        )
        ## dow - transform names to numbers
        quartz_cron_array[5] = re.sub(
            r"\b(" + "|".join(UNIX_DOW.keys()) + r")\b",
            lambda d: UNIX_DOW[d.group(1)],
            quartz_cron_array[5]
        )
    dow = quartz_cron_array[5]

    # year
    ## year - defined
    if len(quartz_cron_array) == 7:
        data_loss.append(DataLossCause.YEAR_WAS_DEFINED)

    return Result(
        unix_cron=f"{minute} {hour} {dom} {month} {dow}",
        quartz_cron=quartz_cron,
        data_loss=data_loss
    )
