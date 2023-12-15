from telegram.ext.filters import Text


PASSWORD = "777jSH"



BACK = "🔙 Ortga"


EXCLUDE = ~Text(["/start", f"/start {PASSWORD}", BACK])


NAME = "NAME"
NUMBER = "NUMBER"
CHECK = "CHECK"
MENU = "MENU"


ADMIN_POST_MEDIA = "ADMIN_POST_MEDIA"
ADMIN_POST_CHECK = "ADMIN_POST_CHECK"
