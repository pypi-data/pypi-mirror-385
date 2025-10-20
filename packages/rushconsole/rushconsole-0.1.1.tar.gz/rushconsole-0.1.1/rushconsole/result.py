class Result:
    def __init__(self, dct):
        for k, v in dct.items():
            setattr(self, k, v)

    def __getitem__(self, item):
        return getattr(self, item, None)

    def __repr__(self):
        result = f'[Result'
        for k, v in self.__dict__.items():
            result += f' {k}={v}'

        return f"{result}]"
