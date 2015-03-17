# ASCII table controller

class Controller:

    def __init__(self,master):
        self.master = master

    def print_ascii_table(self):
            
            import unicodedata
            
            c0_names = [
                'NULL CHAR',
                'START OF HEADING',
                'START OF TEXT',
                'END OF TEXT',
                'END OF TRANSMISSION',
                'ENQUIRY',
                'ACKNOWLEDGMENT',
                'BELL',
                'BACK SPACE',
                'HORIZONTAL TAB',
                'LINE FEED',
                'VERTICAL TAB',
                'FORM FEED',
                'CARRIAGE RETURN',
                'SHIFT OUT / X-ON',
                'SHIFT IN / X-OFF',
                'DATA LINE ESCAPE',
                'DEVICE CONTROL 1 (OFT. XON)',
                'DEVICE CONTROL 2',
                'DEVICE CONTROL 3 (OFT. XOFF)',
                'DEVICE CONTROL 4',
                'NEGATIVE ACKNOWLEDGEMENT',
                'SYNCHRONOUS IDLE',
                'END OF TRANSMIT BLOCK',
                'CANCEL',
                'END OF MEDIUM',
                'SUBSTITUTE',
                'ESCAPE',
                'FILE SEPARATOR',
                'GROUP SEPARATOR',
                'RECORD SEPARATOR',
                'UNIT SEPARATOR'
                ]
            asciitable = []

            for i in xrange(0,128):
                if i < 32:
                    name = c0_names[i]
                elif i < 127:
                    name = unicodedata.name(unicode(chr(i)))
                else:
                    name = 'DELETE'

                asciitable.append({
                    'hex': hex(i)[2:].upper(),
                    'dec': i,
                    'char': chr(i),
                    'unicodename':  name
                    })
                
            self.master.status = 200
            self.master.template_vars.update(asciitable=asciitable)

            
    def run(self):
        if self.master.subrequest:
            return self.master.run_controller('404')
        else:
            self.print_ascii_table()
