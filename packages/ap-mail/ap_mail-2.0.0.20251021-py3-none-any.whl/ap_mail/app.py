import sys

import ut_com.dec as dec
from ut_com.com import Com
from ut_cli.task import Task

from ap_mail.parms import Parms as MailParms
from ap_mail.task import Task as MailTask

from typing import Any

TyTup = tuple[Any, Any]


class App:

    t_parms_task: TyTup = (MailParms, MailTask)

    @classmethod
    @dec.handle_error
    @dec.timer
    def do(cls) -> None:
        Task.do(Com.sh_kwargs(cls, sys.argv))


if __name__ == "__main__":
    App.do()
