from drafter import *
from bakery import assert_equal
from dataclasses import dataclass
from random import randint
from PIL import Image as PIL_Image
import piexif

set_site_information(
    authors: "Micah Johnson (micj@udel.edu), J'nine Hargrove (Jninemh@udel.edu)"
    description= """This project is a MockUp of an app created to lock and unlock 
    private files with ease. The app will be in a taskbar, and will easily allow 
    files to be locked and unlocked using a password."""
    links=["https://github.com/micahlexi22/HenHacks2026_OnLock"]
)
hide_debug_information
set_website_title("OnLock (We Got You!)")
set_website_framed(False)
#set_website_style("skeleton")
set_website_style("tacit")
add_website_css("""
body {
    background-color: lightblue;
    }""")

#dataclasses
@dataclass
class State:
    '''The state variables used throughout the program'''
    file: PIL_Image = "no file selected"
    password: str = "none"
    enter: str = "none"
    intensities: list[int] = field(default_factory = lambda: [255,255,240])
    locked: bool = False
    file_uploaded = bool = False
    entered_password = bool = False
  
#index
@route
def index(state:State)->Page:
    '''Main Page for Website'''
    #resets values after user goes through website the first time
    state.file= "no image selected"
    state.password = ""
    state.file_uploaded = False
    state.entered_password = False
    state.enter = ""
    return Page(state, [
        #Change font sizes and color, check image on site
            Header("Welcome to OnLock!"),
            Image("OnLock_Logo.jpeg"),
            "What would you like to do?",
            change_background_color(Button("LOCK A FILE",locking),"20B2AA"),
            change_background_color(Button("UNLOCK A FILE",unlocking),"20B2AA"),
            change_background_color(Button("LEAVE",leave),"20B2AA"),
            ])
    
#Decoding Functions
def even_or_odd_bit(number:int)->str:
    '''This function consumes an integer and determines if it is odd or even. 
    If it is odd, it returns bit number "1", and if even it returns bit number "0".
        ARGS:
            number(int): The number.
        RETURNS: 
            str: The value representing the bit
    '''
    if number >= 0:
        if number % 2 == 1:
            return "1"
        elif number % 2 != 1:
            return "0"
        else:
            return "error"
    else:
         return "error"

def decode_single_char(intensities: list[int])->str:
    '''Takes in a list of 8 numbers representing the intensities for a single character, and returns that character
        ARGS: 
            intensities(list[int]): A list of 8 intensity values representing the colors of a single character
        RETURNS:
            str: The character represented by the intensity values
    '''
    base = 2
    binary_numbers = ""
    if not intensities:
        return ""
    if len(intensities) != 8:
        return ""
    for intensity in intensities:
        bit_num = even_or_odd_bit(intensity)
        binary_numbers = binary_numbers + bit_num
    ascii_number = int(binary_numbers,base)
    ascii_letter = chr(ascii_number)
    return ascii_letter

def decode_chars(intensities:list[int],num_chars:int)->str:
    '''This function takes a list of 8 intensity values representing a 
    single character and a number of characters, and returns the string of the decoded characters
    ARGS:
        intensities(list[in]):The intensity values for a single character.
        num_chars: The number of characters in the string
    RETURNS:
        str: The string with the decoded characters
        '''
    if len(intensities) != 8 * num_chars:
        return None
    characters = ""
    for i in range(num_chars):
        start = i * 8
        end = start + 8
        characters += decode_single_char(intensities[start:end])
    return characters

def get_message_length(intensities:list[int],num_chars:int)->int:
    '''This function takes a list of 8 intensity values representing a 
    single character and a number of characters, and returns the length of the characters.
    ARGS:
        intensities(list[in]):The intensity values for a single character.
        num_chars: The number of characters in the string
    RETURNS:
        int: The value representing the message.
        '''
    if len(intensities) != 8 * num_chars:
        return 0
    message_length = int(decode_chars(intensities,num_chars))
    return message_length

def get_encoded_message(intensities: list[int])->str:
    '''This function takes a list of intensities and returns the hidden message.
    ARGS:
        intensities(list[in]):The intensity values for a single character.
    RETURNS:
        str: The encoded message.
        '''
    if not intensities:
        return None
    header = 3
    rest_of_message = get_message_length(intensities[0:8*header],header)
    message_length = header + rest_of_message
    message = decode_chars(intensities[0:(message_length)*8],message_length)
    return message[header:]

def get_color_values(image: PIL_Image ,channel:int)-> list[int]:
    '''Function obtains rgb color values from a PILLOW Image
    ARGS:
        image (PIL_Image): The chosen image
        channel: The channel number representing red(0), green(1), or blue(2)
    RETURNS:
        list[int]: The intensity values in the given channel.
        '''
    width, height = image.size
    blue_values = []
    green_values = []
    red_values = []
    if not image:
        return 0
    for x in range(0,width):
        for y in range(0,height):
            red, green ,blue = image.getpixel((x,y))
            red_values.append(red)
            green_values.append(green)
            blue_values.append(blue)
    if channel == 0:
        return red_values
    elif channel == 1:
        return green_values
    elif channel == 2:
        return blue_values
    else:
        return 0
    
#encoding functions
def prepend_header(message:str)->str:
    '''This function takes in a message given by the user and gives the "header" of the message, 
    which tells how many characters are in the message using 3 digits.
        ARGS: 
            message(str): The message given by the user.
        RETURNS:
            str: The header representing how many characters are in the message
            '''
    if not message:
        return "000"+message
    length = str(len(message))
    #Fills the beginning w zeroes up to given amount
    header = length.zfill(3)
    return header + message

def message_to_binary(ascii_chars:str)->str:
    '''Takes in a message containing all ascii characters and 
        returns a binary representation of the string
        ARGS: 
            ascii_chars(str): The message containing ascii characters.
        RETURNS:
            str: The message in binary.
    '''
    if not ascii_chars:
        return "0"
    binary_message = ""
    for character in ascii_chars:
        ascii_num = ord(character)
        binary_char = format(ascii_num,'08b')
        binary_message += binary_char
    return binary_message

def new_color_value(intensity:int,bit_num:str)->int:
    '''Takes in an in representing the base 10 intensity value 
    and the single bit that needs to be hidden, and 
    returns the new base 10 color intensity.
    ARGS:
        intensity(int): The original Base 10 color intensity value.
        bit_num(str): The bit that needs to be hidden.
    RETURNS:
        int: The new hidden Base 10 intensity value.
    '''
    new_intensity = 0
    if bit_num == "1" :
        if intensity % 2 != 1: #even
            new_intensity = intensity + 1
        else: #odd
            new_intensity = intensity
    elif bit_num == "0":
        if intensity % 2 != 1: #even
            new_intensity = intensity
        else:#odd
            new_intensity = intensity - 1     
    return new_intensity

def hide_bits(image: PIL_Image,binary_message:str)->PIL_Image:
    '''Consumers a Pillow Image and hides message by 
    changing the color intesity of the bits 
    *in green channel only
    ARGS:
        image(PIL_Image): The uploaded image
        binary_message(str): The hidden message, changed to binary
    RETURNS:
        PIL_Image: The updated image with the message hidden
     '''
    width, height = image.size
    if not image:
        return 0
    index = 0
    for x in range(0,width):
        for y in range(0,height):
            red, green ,blue = image.getpixel((x,y))
            updated_green = new_color_value(green,binary_message[index])
            image.putpixel((x,y),(red,updated_green,blue))
            index += 1
            if index >= len(binary_message):
                return image
    return image

def encode_message(message:str)->str:
    """ main function for hiding a message in an image file
    Args:
        message(str): The message being hidden in the file
    Return:
        str: The binary string of the hidden message
    """
    message_with_header = prepend_header(message)
    message_in_binary = message_to_binary(message_with_header)
    return message_in_binary

#routes
@route
def leave(state: State) -> Page:
    """Leaving the website"""
    return Page(state,[
            Header("Thank you for using the website!"),
            "Goodbye!"
            ])
@route
def locking(state:State)->Page:
    '''User can select a file to lock'''
    state.locked = False
    return Page(state,[
        Header("LOCK FILE"),
        "Please Choose A file You Would Like To Lock",
        change_background_color(Button("SELECT FILE",fileupload),"20B2AA"),
        change_background_color(Button("MAIN MENU",index),"20B2AA")
        ])

@route
def unlocking(state:State)->Page:
    '''User can select a file to unlock'''
    state.locked = True
    return Page(state,[
        Header("UNLOCK FILE"),
        "Please Choose A file You Would Like To Unlock",
        change_background_color(Button("SELECT FILE",fileupload),"20B2AA"),
        change_background_color(Button("MAIN MENU",index),"20B2AA")
        ])
  #See if you can try other filetypes          
@route
def fileupload(state: State)-> Page:
    """Allow user to select encoded png files to upload"""
    if state.locked == False:
        return Page(state, [
            Header("UPLOAD FILE"),
            "Select a 'png' file.",
            FileUpload("new_image",accept = "image/png"),
            change_background_color(Button("SHOW FILE",chosen_file),"20B2AA"),
            change_background_color(Button("BACK",locking),"20B2AA")
            ])
    elif state.locked == True:
        return Page(state, [
            Header("UPLOAD FILE"),
            "Select a 'png' file.",
            FileUpload("new_image",accept = "image/png"),
            change_background_color(Button("SUBMIT FILE",chosen_file),"20B2AA"),
            change_background_color(Button("BACK",unlocking),"20B2AA")
            ])

@route
def chosen_file(state:State, new_image: bytes)-> Page:
    '''Assigns file to State field'''
    state.file = PIL_Image.open(io.BytesIO(new_image)).convert('RGB')
    state.file_uploaded = True
    if state.locked == False:
        return Page(state, [
                "Confirm Uploaded File",
                Image(state.file),
                change_background_color(Button("CHANGE FILE",fileupload),"20B2AA"),
                change_background_color(Button("CONFIRM FILE", create_password),"20B2AA")
                ])
    elif state.locked == True:
        return Page(state, [
                "Confirm Uploaded File",
                change_background_color(Button("CHANGE FILE",fileupload),"20B2AA"),
                change_background_color(Button("CONFIRM FILE", enter_password),"20B2AA")
                ])
    
#@route
#def change_thumbnail(state: State)->Page:
    #'''Changes file thumbnail to lock icon'''
    #if state.locked == False:
    #    im = Image.open(state.file)
     #   thumb_im = Image.open("lock.jpeg")
     #   thumb_im.thumbnail((64,64), Image.Resampling.LANCZ0S)
     #   output_bytes = io.BytesI0()
      #  thumb_im.save(output_bytes, "png")
     #   thumbnail_bytes = output_bytes.getvalue()
      #  exif_dict = piexif.load(im.info['exif']) if 'exif' in im.info else {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}
      #  exif_dict["thumbnail"] = thumbnail_bytes
      #  exif_bytes = piexif.dump(exif_dict)
       # im.save(state.file, exif=exif_bytes)
      #  return locked_file(state)
    #else:
     #   im = Image.open(state.file)
     #   thumb_im = Image.open(state.file)
     #   thumb_im.thumbnail((64,64), Image.Resampling.LANCZ0S)
     #   output_bytes = io.BytesI0()
     #   thumb_im.save(output_bytes, "png")
      #  thumbnail_bytes = output_bytes.getvalue()
      #  exif_dict = piexif.load(im.info['exif']) if 'exif' in im.info else {"0th":{}, "Exif":{}, "GPS":{}, "1st":{}, "thumbnail":None}
       # exif_dict["thumbnail"] = thumbnail_bytes
      #  exif_bytes = piexif.dump(exif_dict)
      #  im.save(state.file, exif=exif_bytes)
      #  return unlock(state)
 
@route
def create_password(state: State)->Page:
    '''Allows user to create a Password to lock file'''
    return Page(state, [
        "Please Create a Password: ",
        TextBox("new_message", state.password),
        change_background_color(Button("BACK",locking),"20B2AA"),
        change_background_color(Button("SHOW PASSWORD", save_password),"20B2AA")
        ])
@route   
def save_password(state: State,new_message:str)-> Page:
    '''Saves user's message into state field'''
    if len(state.password) <= 100:
       state.password = new_message
       state.entered_password = True
       return Page(state, [
       "Confirm New Message : ",
       state.password,
       change_background_color(Button("CHANGE MESSAGE",create_password),"20B2AA"),
       change_background_color(Button("CONFIRM PASSWORD", lock),"20B2AA")
       ])
    else:
        return Page(state, [
        "Your message does not meet criteria, please try again!",
        change_background_color(Button("CREATE PASSWORD", create_password),"20B2AA")
        ])
 #Find a way to change thumbnail of file   
@route
def lock(state:State)-> Page:
    '''Allows user to encode a message into png image'''
    if not state.file_uploaded:
        return fileupload(state)
    elif not state.file_uploaded:
        return enter_file(state)
    elif state.file_uploaded and state.entered_password:
        message_binary = encode_message(state.password)
        state.file = hide_bits(state.file,message_binary)
        #return change_thumbnail(state)
        return locked_file(state)
@route
def locked_file(state:State)->Page:
    '''Allows the user to download the encoded image file'''
    filename = str(randint(1,100)) + "_file"
    state.locked = True
    return Page(state, [
        "Your file, " + filename + " ,has been locked!",
        Download("Download File",filename,state.file),
        change_background_color(Button("MAIN MENU",index),"20B2AA")
        ])

@route
def enter_password(state:State) -> Page:
    '''Sees if password is equal to the set password encoded in the file'''
    return Page(state, [
        "Please Enter Password: ",
        TextBox("message", state.enter),
        change_background_color(Button("BACK",unlocking),"20B2AA"),
        change_background_color(Button("SUBMIT PASSWORD", unlock),"20B2AA")
        ])

@route
def unlock(state: State)-> Page:
    '''Unlocks locked file'''
    if state.enter == state.password:
        state.locked = False
        return Page(state, [
           "Your file is unlocked!",
           Image(state.file),
           change_background_color(Button("MAIN MENU",index),"20B2AA")
           ])
    else:
        return Page(state, [
            "The password does not match. Try again!",
            change_background_color(Button("RE-ENTER PASSWORD",enter_password),"20B2AA"),
            change_background_color(Button("MAIN MENU",index),"20B2AA")
            ])
  
start_server(State())
