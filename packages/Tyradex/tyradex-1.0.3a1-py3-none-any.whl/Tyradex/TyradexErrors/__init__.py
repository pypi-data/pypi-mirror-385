import pratik.text


class TyradexError(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    def __str__(self):
        return str(self.__class__.__name__) + ' : ' + ', '.join(self.args)

    def print(self):
        print(pratik.text.Color.RED + str(self) + pratik.text.Color.STOP)

class PageNotFound(TyradexError):
    def __init__(self, endpoint=''):
        super().__init__(
            "The page{endpoint} was not found"
            .format(
                endpoint=(' "' + endpoint + '"') if endpoint != '' else ''
            )
        )