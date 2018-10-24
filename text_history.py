class TextHistory:
    def __init__(self, pos=None, text='', length=None):
        self._text = text
        self._version = 0
        self._list = []

    @property
    def version(self):
        return self._version

    @property
    def text(self):
        return self._text

    def insert(self, text, pos=None):
        if pos == None:
            pos = len(str(self._text))
        if pos > len(str(self._text)) or pos < 0:
            raise ValueError
        self._version += 1
        insert = InsertAction(text = text, pos = pos, from_version = (self._version-1),
                               to_version = self._version )
        self._text = insert.apply(self._text)#
        self._list.append(insert)
        return self._version
    
    def delete(self, length, pos=None):
        if pos == None:
            pos = len(str(self._text))
        if (pos > len(str(self._text)) or pos < 0
            or (pos+length)>len(str(self._text))):
            raise ValueError
        self._version += 1
        delete = DeleteAction(text = self._text, pos=pos, length=length,
                              from_version = (self._version-1), to_version = self._version )
        self._text = delete.apply(text=self._text)
        self._list.append(delete)
        return self._version

    def replace(self, text, pos=None):
        if pos == None:
            pos = len(str(self._text))
        if pos > len(str(self._text)) or pos < 0:
            raise ValueError
        self._version += 1
        replace = ReplaceAction(text = text, pos = pos, from_version = (self._version-1),
                                 to_version = self._version )
        self._text = replace.apply(self._text)
        self._list.append(replace)
        return self._version
    
    def action(self, action):
        if ((action._from_version == action._to_version) or
            (self._version != action._from_version)):
            raise ValueError
        self._version = action._to_version
        self._text = action.apply(self._text)
        differ = action._to_version - action._from_version
        if (differ)>1:
            for i in range(action._from_version, differ):
                self._list.append(None)
        self._list.append(action)
        return self._version
    
    def get_actions(self, from_version = 0, to_version = None):
        if to_version == None:
            to_version = self._version
        if from_version < 0 or to_version > self._version or from_version > to_version:
            raise ValueError
        #В случае, если подряд идёт несколько операий insert в начале строки,
        #заменяем их на одну, которая вставляет текст всех предыдущих. Остальные - None
        buff = []
        i = 0
        for obj in self._list:
            if i>0:
                if obj.pos == 0 and buff[i-1].pos == 0 and type(obj)==type(buff[i-1])==InsertAction:
                    (self._list[i]).text=(self._list[i]).text + (self._list[i-1]).text
                    self._list[i-1]=None
            i+=1
            buff.append(obj)
        #В случае, если подряд идёт несколько операий delete в начале строки,
        #заменяем их на одну, которая удаляет текста на суммарную длину всех операций. Остальные - None
        buff = []
        i = 0
        for obj in self._list:
            if i>0:
                if obj.pos == 0 and buff[i-1].pos == 0 and type(obj)==type(buff[i-1])==DeleteAction:
                    (self._list[i]).length=(self._list[i-1]).length+(self._list[i]).length
                    self._list[i-1]=None
            i+=1
            buff.append(obj)
        output = self._list[from_version:to_version]
        return output

class Action:
    def __init__(self, pos=None, length=None, text='', from_version=None, to_version=None):
        self._pos = pos
        self._length = length
        self._text = text
        self._to_version = to_version
        self._from_version = from_version

    @property
    def text(self):
        return self._text
    @text.setter
    def text(self, value):
        self._text = value
    @property
    def from_version(self):
        return self._from_version
    @property
    def to_version(self):
        return self._to_version
    @property
    def pos(self):
        return self._pos
    @property
    def length(self):
        return self._length
    @length.setter
    def length(self, value):
        self._length = value
    
class InsertAction(Action):
    def apply(self, text):
        return text[:self._pos]+self._text+text[self._pos:]

class DeleteAction(Action):
    def apply(self, text=None):
        return text[:self._pos]+text[self._pos+self._length:]
    
class ReplaceAction(Action):
    def apply(self, text):
        return text[:self._pos]+self._text+text[self._pos+len(self._text):]
