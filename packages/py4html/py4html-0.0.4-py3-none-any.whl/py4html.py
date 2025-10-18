import atexit
import threading
import queue
import os
import inspect
import re

file_pointer_position=0
html_file_name=""

def create_html_file():
    # Get the last frame in the stack, which corresponds to the importing module
    global html_file_name
    frame = inspect.stack()[-1]
    importing_file_path = frame.filename  # Full path of the importing file
    # Extract name without extension
    importing_file_name = os.path.splitext(os.path.basename(importing_file_path))[0]  
    html_file_name=importing_file_name+"_.html"

create_html_file()  
f=open(html_file_name,'w')
   
start_string = """<!DOCTYPE html>
<html>
<head>
<style>
</style>
</head>
<body>
"""
end_string = """
</body>
</html>
""" 

f.write(start_string)

file_lock=threading.Lock()

def stylizer(element,style):
    styled_string= f'<{element}  style="'
    for item in style:
        styled_string=styled_string + f"{item}:{style[item]}; "
    styled_string=styled_string + '">'
    return styled_string


def style_copier(css_code_string):
    css_dic={}
    inside_key=True
    inside_value=True
    key_start_index=0
    while '/*' in css_code_string and '*/' in css_code_string:
        start = css_code_string.find('/*')  # Find the start of the comment
        end = css_code_string.find('*/', start)  # Find the end of the comment
        if end == -1:
            break
        css_code_string = css_code_string[:start] + css_code_string[end + 2:]  # Remove the comment block
    
    for i,ch in enumerate(css_code_string):
        if ch == ":" and inside_key==True:
            inside_key=False
            key=css_code_string[key_start_index:i]
            key_end_index=i+1
            inside_value=True
        if ch==";" and inside_value == True:
            value=css_code_string[key_end_index:i]
            inside_value==False
            inside_key=True
            key_start_index=i+1
            key=key.strip()
            value=value.strip()
            css_dic[key]=value
           
    return css_dic


def read_file_again_separate_thread(q):
    with file_lock:
        with open(html_file_name,"r") as rf:
            lines = rf.readlines()
            q.put(lines)

def edit_file_4style(style_dict):
    global file_pointer_position
    f.flush()
    q=queue.Queue()
    new_thread4_reading=threading.Thread(target=read_file_again_separate_thread,args=(q,))
    new_thread4_reading.start()
    new_thread4_reading.join()
    # Get the file content from the queue
    lines_from_queue = q.get()
    lines=[]
    #print("\nFile content read by the separate thread:")
    for line in lines_from_queue:
        lines.append(line)
    # Define the word to search for and the text to insert
    search_word = "<style>"
    text_to_insert = ""
    text_to_insert=','.join(next(iter(style_dict)))
    text_to_insert=text_to_insert+"{\n"
    value_dict=next(iter(style_dict.values()))
    for individual_style in value_dict:
        text_to_insert=text_to_insert+f"{individual_style}:{value_dict[individual_style]}; " + "\n"
    text_to_insert=text_to_insert + "}\n"

    # Flag to indicate whether we've found the target line
    found = False
    # Loop through the lines
    for i, line in enumerate(lines):
        if line.startswith(search_word):
            # Insert the new line after the found line
            lines.insert(i + 1, text_to_insert)
            found = True
            break

    # Only write if we found the line and modified the content
    if found:
        with file_lock:
            with open(html_file_name, "w") as file:
                #file.seek(file_pointer_position)
                file.writelines(lines)
                file.flush()
                file_pointer_position=file.tell()
            
def edit_file_4title(title_text):
    global file_pointer_position
    f.flush()
    tq=queue.Queue()
    new_titlethread4_reading=threading.Thread(target=read_file_again_separate_thread,args=(tq,))
    new_titlethread4_reading.start()
    new_titlethread4_reading.join()
    # Get the file content from the queue
    lines_from_queue = tq.get()
    lines=[]
    #print("\nFile content read by the separate thread:")
    for line in lines_from_queue:
        lines.append(line)

    # Define the word to search for and the text to insert
    search_word = "<head>"
    text_to_insert=f"<title>\n{title_text}\n</title>\n"

    # Flag to indicate whether we've found the target line
    found = False
    # Loop through the lines
    for i, line in enumerate(lines):
        if line.startswith(search_word):
            # Insert the new line after the found line
            lines.insert(i + 1, text_to_insert)
            found = True
            break
    # Only write if we found the line and modified the content
    if found:
        with file_lock:
            with open(html_file_name, "w") as file:
                #file.seek(file_pointer_position)
                file.writelines(lines)
                file.flush()
                file_pointer_position=file.tell()

def title(title_text):
    title_thread=threading.Thread(target=edit_file_4title,args=(title_text,))
    title_thread.start()
    title_thread.join()
    f.seek(file_pointer_position)
    f.write("\n")

def edit_file_4allstyles(style_dict):
    global file_pointer_position
    f.flush()
    all_styles_queue=queue.Queue()
    new_thread4_reading=threading.Thread(target=read_file_again_separate_thread,args=(all_styles_queue,))
    new_thread4_reading.start()
    new_thread4_reading.join()
    # Get the file content from the queue
    lines_from_queue = all_styles_queue.get()
    lines=[]
    #print("\nFile content read by the separate thread:")
    for line in lines_from_queue:
        lines.append(line)
    # Define the word to search for and the text to insert
    search_word = "<style>"
    text_to_insert=""
    for entry in style_dict:
        text_to_insert=text_to_insert+f"{entry}"+"{\n"
        individual_style=style_dict[entry]
        for element in individual_style:
            text_to_insert=text_to_insert + f"{element}:{individual_style[element]};\n"
        text_to_insert=text_to_insert+"}\n"
    # Flag to indicate whether we've found the target line
    found = False
    # Loop through the lines
    for i, line in enumerate(lines):
        if line.startswith(search_word):
            # Insert the new line after the found line
            lines.insert(i + 1, text_to_insert)
            found = True
            break
    # Only write if we found the line and modified the content
    if found:
        with file_lock:
            with open(html_file_name, "w") as file:
                #file.seek(file_pointer_position)
                file.writelines(lines)
                file.flush()
                file_pointer_position=file.tell()

def all_styles(style_dic):
    allstyles_thread=threading.Thread(target=edit_file_4allstyles,args=(style_dic,))
    allstyles_thread.start()
    allstyles_thread.join()
    f.seek(file_pointer_position)
    f.write("\n")

def transform_text(text,text_type):
    match text_type:
        case "bold":text="<b>"+text+"</b>"
        case "important":text="<strong>"+text+"</strong>"
        case "italics":text="<i>"+text+"</i>"
        case "emphasized":text="<em>"+text+"</em"
        case "mark":text="<mark>"+text+"</mark>"
        case "small":text="<small>"+text+"</small>"
        case "deleted":text="<del>"+text+"</del>"
        case "inserted":text="<ins>"+text+"</ins>"
        case "sub":text="<sub>"+text+"</sub>"
        case "sup":text="<sup>"+text+"</sup>"
    return text


def heading(text,num=1,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start=f"h{num}"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h{num}>\n")

def biggest_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h1"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h1>\n")

def bigger_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h2"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h2>\n")

def big_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h3"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h3>\n")

def small_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h4"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h4>\n")

def smaller_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h5"
    if id:
        start=start + f" {id}"
    if class_name:
        start=start + f" {class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h5>\n")

def smallest_heading(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="h6"
    if id:
        start=start + f" id={id}"
    if class_name:
        start=start + f" class={class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    f.write(f"{starting}\n{text}\n</h6>\n")


def paragraph(text,text_type="",style={},id="",class_name="",attr_list=[]):
    if text_type:
        text=transform_text(text,text_type)
    start="p"
    if id:
        start=start + f" id={id}"
    if class_name:
        start=start + f" class={class_name}"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        starting=stylizer(start,style)
    else:
        starting="<"+start+">"
    if text.endswith("##"):
        if text[-3]=="\\":
            f.write(f"{starting}\n{text[:-3]+"##"}\n</p>\n")
        else:
            return f"{starting}\n{text[:-2]}\n</p>\n"

    else:
        f.write(f"{starting}\n{text}\n</p>\n")


def line_break():
    f.write("<br>\n")

   
def division_begins(style={},text="",id="",class_name="",attr_list=[]):
    div_string=""
    type="write"
    return_string=""
    if class_name:
        div_string=f'<div class ="{class_name}"'
        if class_name.endswith("##"):
            type="return"
    elif id:
        div_string=f'<div id ="{id}"' 
        if id.endswith("##"):
            type="return"  
    else:
        div_string="<div"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        div_string=div_string+attr_string  
    if style:
        div_string=div_string + '  style="'
        style_string=""
        for item in style:
            style_string=style_string + f"{item}:{style[item]}; "
        div_string=div_string + style_string + '"'
    if type=="write":
        f.write(div_string + ">"+ "\n")
    else:
        return_string=div_string + ">"+ "\n"
        
    if text:
        if type=="write":
            f.write(text+'\n')
        else:
            return_string=return_string+text+"\n"
            return_string=return_string + "</div>"
    return return_string


def division_ends():
    f.write("</div>\n")


def add_link(link_text,url,style={},attr_list=[]):
    starting=f'a href="{url}"'
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        starting=starting+attr_string  
    if style:
        starting=stylizer(starting,style)
    else:
        starting="<" + starting + ">"
    if link_text.endswith("##"):
        if link_text[-3]=="\\":
            f.write(f'{starting}{link_text[:-3]+"##"}</a>\n')
        else:
            return f'{starting}{link_text[:-2]}</a>\n'

    else:
        f.write(f'{starting}{link_text}</a>\n')
    
    
def unordered_list(*items):
    first="no"
    if type(items[0]) is dict:
        styled_stirng=stylizer("ul",items[0])
        f.write(styled_stirng+"\n")
        first="yes"
    else:
        f.write('<ul>\n')
    if first =="yes":
        basket=items[1:]
    else:
        basket=items
    print_list=[]
    list_count=0
    for i,item in enumerate(basket):
        if type(item) is dict:
            styled_stirng=stylizer("li",item)
            print_list[list_count-1]=f"{styled_stirng}{basket[i-1]}</li>\n"
            
        else:
            print_list.append(f"<li>{item}</li>\n")
            list_count+=1
            
    for line in print_list:
        f.write(line)
    f.write('</ul>\n')

def ordered_list(*items,attr_list=[]):
    first="no"
    start="ol"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if type(items[0]) is dict:
        styled_stirng=stylizer(start,items[0])
        f.write(styled_stirng+"\n")
        first="yes"
    else:
        f.write('<'+start+'>\n')
    if first =="yes":
        basket=items[1:]
    else:
        basket=items
    print_list=[]
    list_count=0
    for i,item in enumerate(basket):
        if type(item) is dict:
            styled_stirng=stylizer("li",item)
            print_list[list_count-1]=f"{styled_stirng}{basket[i-1]}</li>\n"
            
        else:
            print_list.append(f"<li>{item}</li>\n")
            list_count+=1
            
    for line in print_list:
        f.write(line)
    f.write('</ol>\n')

def description_list(items,style={}):
    if style:
        style_applied=stylizer("dl",style)
        f.write(style_applied)
    else:
        f.write('<dl>\n')
    for item in items:
        f.write(f"<dt>{item}</dt>\n")
        f.write(f"<dd>{items[item]}</dd>\n")
    f.write('</dl>\n')  


def table(items_list,style={},attr_list=[]):
    global file_pointer_position
    start="table"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        start_string=stylizer(start,style)+'\n'
    else:
        start_string='<'+start+'>\n'
    f.write(start_string)
    skip=False
    if type(items_list[0]) is tuple:
        headings=items_list[0]
        skip=True
        f.write("<tr>\n")
        for heading in headings:
            f.write(f'<th>{heading}</th>\n')
        f.write("</tr>\n")
        
    row_list=[]
    element_list2d=[]
    content_list=[]
    for n,row in enumerate(items_list):
        if skip:
            skip=False
            n=n-1
            continue
        if type(row) is dict:
            if "rowspan" in row:
                row_list[n-1]=f"<tr rowspan={row["rowspan"]}>"
                del row["rowspan"]
            row_list[n-1]=stylizer("tr",row)+"\n"
        else:
            row_list.append("<tr>\n")
            
        elements_in_one_row=[]
        content_in_one_row=[]
        n=0
        for element in row:
            if type(element) is dict:
                if "common_style" in element:
                    separate_thread=threading.Thread(target=edit_file_4style,args=(element["common_style"],))
                    separate_thread.start()
                    separate_thread.join()
                    f.seek(file_pointer_position)
                    elements_in_one_row.append("<td>\n")
                    continue
                if "colspan" in element:
                    span_value=element["colspan"]
                    del element["colspan"]
                    if element:
                        styled_string=stylizer("td",element)+"\n"
                        ind=styled_string.index(" ")
                        final_string=styled_string[:ind]+f"colspan={span_value} " + styled_string[ind:]
                        elements_in_one_row[n-1]=final_string
                    else:
                        elements_in_one_row[n-1]=f'<td colspan="{span_value}" >'
                    
                if "rowspan" in element:
                    span_value=element["rowspan"]
                    del element["rowspan"]
                    if element:
                        styled_string=stylizer("td",element)+"\n"
                        ind=styled_string.index(" ")
                        final_string=styled_string[:ind]+f"rowspan={span_value} " + styled_string[ind:]
                        elements_in_one_row[n-1]=final_string
                    else:
                        elements_in_one_row[n-1]=f'<td rowspan="{span_value}" >'
            
            elif type(element) is tuple:
                elements_in_one_row.append("<th>\n")
                content_in_one_row.append(element[0])
        
            else:
                elements_in_one_row.append("<td>\n")
                content_in_one_row.append(element)
        element_list2d.append(elements_in_one_row)
        content_list.append(content_in_one_row)
    
    #writing to html file
    for ln,row in enumerate(row_list):
        f.write(row)
        for tag,content in zip(element_list2d[ln],content_list[ln]):
            f.write(tag)
            f.write(content+"\n")
            if "td" in tag:
                f.write('</td>\n')
            else:
                f.write('</th>')
        f.write("</tr>\n")
    f.write("</table>\n")


class form():
    '''
    def __init__(self,**arguments):
        sent_arguments=()
        for argument in arguments:
            arg_name=f"{argument}={arguments[argument]}"
            arg_name=arg_name.strip("'")
            sent_arguments=sent_arguments+(arg_name,)
            print(sent_arguments)
        self.start(*sent_arguments)
    '''    
    def __init__(self,action=" ",method="",style={},attr_list=[]):
        if action:
            start=f"form action=\"{action}\" "
            if method:
                 start=f"form action=\"{action}\" method='{method}' "
            if attr_list:
                attr_string=""
                for attr in attr_list:
                    attr_string=attr_string + f"{attr}" + " "
                start=start+attr_string 
            
        elif method:
            start=f"form method='{method}' " #simply added to avoid error in Python eventhough it should not be used
        elif attr_list:
                attr_string=""
                for attr in attr_list:
                    attr_string=attr_string + ' ' + f"{attr}"
                start=start+attr_string                                  
        else:
            start="form"
        if style:
            styled_string=stylizer(start,style)
            f.write(styled_string+'\n')
        else:
            f.write("<"+ start +">\n")

    def label(self,text,id="",style={},attr_list=[]):
        start=f"label for=\"{id}\""
        if attr_list:
            attr_string=""
            for attr in attr_list:
                attr_string=attr_string + ' ' + f"{attr}"
            start=start+attr_string  
        if style:
             styled_string=stylizer(start,style)
             f.write(f"{styled_string}{text}</label>\n")
        else:    
            f.write(f"<label for=\"{id}\">{text}</label>\n")

    def input(self,type="",id="",name="",value="",style={},attr_list=[],radio_button_list=[],
              radio_attribute_list=[],radio_style_list=[],radio_label_attribute_list=[],radio_label_style_list=[],
              checkbox_list=[],checkbox_attribute_list=[],checkbox_style_list=[],check_label_attribute_list=[],
              check_label_style_list=[]):
        if type=="text":
            start=f"input type=\"text\" id=\"{id}\" name=\"{name}\" value=\"{value}\""
            if attr_list:
                attr_string=""
                for attr in attr_list:
                    attr_string=attr_string + ' ' + f"{attr}"
                start=start+attr_string

            if style:
                styled_string=stylizer(start,style)
                f.write(f"{styled_string}\n")
            else:    
                f.write("<"+start+">\n")

        elif type=="submit":
            start=f"input type=\"submit\" value=\"{value}\""
            if attr_list:
                attr_string=""
                for attr in attr_list:
                    attr_string=attr_string + ' ' + f"{attr}"
                start=start+attr_string  
            if style:
                styled_string=stylizer(start,style)
                f.write(f"{styled_string}\n")
            else:    
                f.write("<"+start+">\n")
        
        #To apply style to individual radio input entries and labels,use nested lists and dictionaries
        #with attribute list and style dictionary at the exact position or number of the radio or label to be styled
        #and empty lists and dictionaries at every other position
        elif type=="radio":
            for id,label in enumerate(radio_button_list):
                start=f'input type="radio" id="{label.rstrip("#")}{id}" name="{"radio"+radio_button_list[0].rstrip("#")}" value="{label.rstrip("#")}"'
                if radio_attribute_list:
                    radio_attr_string=""
                    for attr in radio_attribute_list:
                        radio_attr_string=radio_attr_string + ' ' + f"{attr}"
                    start=start+radio_attr_string 
                
                if len(radio_style_list)>=1:
                    styled_string=stylizer(start,radio_style_list[id])
                    f.write(f"{styled_string}\n")
                else:    
                    f.write("<"+start+">\n")

                start=f'label for="{label.rstrip("#")}{id}"'
                if radio_label_attribute_list:
                    label_attr_string=""
                    for attr in radio_label_attribute_list:
                        label_attr_string=label_attr_string + ' ' + f"{attr}"
                    start=start+label_attr_string  
                if len(radio_label_style_list)>=1:
                    styled_string=stylizer(start,radio_label_style_list[id])
                    # use ## to add a single line break after a label
                    if label.endswith("##"):
                        match=re.search('#*$',label)
                        total=len(match.group(0))
                        count=total//2
                        f.write(f"{styled_string}{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                    else:
                        f.write(f"{styled_string}{label}</label>\n")
                else:
                    if label.endswith("##"):
                        match=re.search('#*$',label)
                        total=len(match.group(0))
                        count=total//2
                        f.write("<" + start +f">{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                    else:
                        f.write("<" + start +f">{label}</label>\n")

        elif type=="checkbox":
            for id,label in enumerate(checkbox_list):
                start=f'input type="checkbox" id="{label.rstrip("#")}{id}" name="{"check"+checkbox_list[0].rstrip("#")}" value="{label.rstrip("#")}"'
                if checkbox_attribute_list:
                    checkbox_attr_string=""
                    for attr in checkbox_attribute_list:
                        checkbox_attr_string=checkbox_attr_string + ' ' + f"{attr}"
                    start=start+checkbox_attr_string 
                
                if len(checkbox_style_list)>=1:
                    styled_string=stylizer(start,checkbox_style_list[id])
                    f.write(f"{styled_string}\n")
                else:    
                    f.write("<"+start+">\n")

                start=f'label for="{label.rstrip("#")}{id}"'
                if check_label_attribute_list:
                    label_attr_string=""
                    for attr in check_label_attribute_list:
                        label_attr_string=label_attr_string + ' ' + f"{attr}"
                    start=start+label_attr_string  
                if len(check_label_style_list)>=1:
                    styled_string=stylizer(start,check_label_style_list[id])
                    # use ## to add a single line break after a label
                    if label.endswith("##"):
                        match=re.search('#*$',label)
                        total=len(match.group(0))
                        count=total//2
                        f.write(f"{styled_string}{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                    else:
                        f.write(f"{styled_string}{label}</label>\n")
                else:
                    if label.endswith("##"):
                        match=re.search('#*$',label)
                        total=len(match.group(0))
                        count=total//2
                        f.write("<" + start +f">{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                    else:
                        f.write("<" + start +f">{label}</label>\n")
        
        else:
            start=f"input type=\"{type}\" id=\"{id}\" value=\"{value}\""
            if attr_list:
                attr_string=""
                for attr in attr_list:
                    attr_string=attr_string + ' ' + f"{attr}"
                start=start+attr_string  
            if style:
                styled_string=stylizer(start,style)
                f.write(f"{styled_string}\n")
            else:    
                f.write("<"+start+">\n")

    def fieldset(self,legend="",style={},attr_list=[],radio_button_list=[],
              radio_attribute_list=[],radio_style_list=[],radio_label_attribute_list=[],radio_label_style_list=[],
              checkbox_list=[],checkbox_attribute_list=[],checkbox_style_list=[],check_label_attribute_list=[],
              check_label_style_list=[]):
        
        start="fieldset"
        if attr_list:
            attr_string=""
            for attr in attr_list:
                attr_string=attr_string + ' ' + f"{attr}"
            start=start+attr_string  
        if style:
            styled_string=stylizer(start,style)
            f.write(f"{styled_string}\n")
        else:    
            f.write("<"+start+">\n")
        
        if legend:
             f.write(f"<legend>{legend}</legend>\n")
        
        if radio_button_list:
            for id,label in enumerate(radio_button_list):
                    start=f'input type="radio" id="{label.rstrip("#")}{id}" name="{"radio"+radio_button_list[0].rstrip("#")}" value="{label.rstrip("#")}"'
                    if radio_attribute_list:
                        radio_attr_string=""
                        for attr in radio_attribute_list:
                            radio_attr_string=radio_attr_string + ' ' + f"{attr}"
                        start=start+radio_attr_string 
                    
                    if len(radio_style_list)>=1:
                        styled_string=stylizer(start,radio_style_list[id])
                        f.write(f"{styled_string}\n")
                    else:    
                        f.write("<"+start+">\n")

                    start=f'label for="{label.rstrip("#")}{id}"'
                    if radio_label_attribute_list:
                        label_attr_string=""
                        for attr in radio_label_attribute_list:
                            label_attr_string=label_attr_string + ' ' + f"{attr}"
                        start=start+label_attr_string  
                    if len(radio_label_style_list)>=1:
                        styled_string=stylizer(start,radio_label_style_list[id])
                        # use ## to add a single line break after a label
                        if label.endswith("##"):
                            match=re.search('#*$',label)
                            total=len(match.group(0))
                            count=total//2
                            f.write(f"{styled_string}{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                        else:
                            f.write(f"{styled_string}{label}</label>\n")
                    else:
                        if label.endswith("##"):
                            match=re.search('#*$',label)
                            total=len(match.group(0))
                            count=total//2
                            f.write("<" + start +f">{label[:(-2*count)]}</label>"+"<br>"*count+"\n")
                        else:
                            f.write("<" + start +f">{label}</label>\n")
        elif checkbox_list:
            self.input(type="checkbox",checkbox_list=checkbox_list,checkbox_attribute_list=checkbox_attribute_list,
                       checkbox_style_list=checkbox_style_list,check_label_attribute_list=check_label_attribute_list,
              check_label_style_list=check_label_style_list)

        f.write("</fieldset>\n")
                
    def close(self):
        f.write("</form>\n")        


def image(source,alternate_text="",style={},attr_list=[]):
    send_to_stylizer=f'img src="{source}" alt="{alternate_text}"'
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        send_to_stylizer=send_to_stylizer+attr_string  
    if style:
        starting=stylizer(send_to_stylizer,style)
    else:
        starting="<" + send_to_stylizer
    if source.endswith("##"):
        if source[-3]=="\\":
            first=starting.find("src")
            last=starting.find("\\",first)
            substituted_string=starting[first:last]
            replaced_string=starting[first:last+3]
            starting=starting.replace(replaced_string,substituted_string)
            f.write(f"{starting}>\n")
        else:
            first=starting.find("src")
            last=starting.find("##",first)
            substituted_string=starting[first:last]
            replaced_string=starting[first:last+2]
            starting=starting.replace(replaced_string,substituted_string)
            return f"{starting}>\n"

    else:
        f.write(f"{starting}>\n")


def video(source={},style={},attr_list=[],no_video_text=""):
    start="video"
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        styled_string=stylizer(start,style)
        f.write(f"{styled_string}\n")
    else:    
        f.write("<"+start+">\n")
    for video in source:
        f.write(f"<source src=\"{video}\" type=\"{source[video]}\">\n")
    f.write(no_video_text+"\n")
    f.write("</video>")

def button(name_on_button,attr_list=[],style={}):
    start="button "
    if attr_list:
        attr_string=""
        for attr in attr_list:
            attr_string=attr_string + ' ' + f"{attr}"
        start=start+attr_string  
    if style:
        styled_string=stylizer(start,style)
        f.write(f"{styled_string}\n")
    else:    
        f.write("<"+start+">\n")
    f.write(name_on_button+"\n")
    f.write("</button>\n")


def remove_blank_lines_inplace(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()  # Read all lines
    
    # Remove blank lines
    non_empty_lines = [line for line in lines if line.strip()]
    
    # Write back to the same file
    with open(filename, 'w') as file:
        file.writelines(non_empty_lines)

        
@atexit.register
def end():
        f.write(end_string)
        f.close()
        remove_blank_lines_inplace(html_file_name)