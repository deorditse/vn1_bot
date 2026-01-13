## CONVERT MARKDOWN TO MENU HTML

1. Each Markdown heading must be a single menu item according to the following rules:
    ``` html
    <li>
      <a href="#anchorId" class="product-details-instructions-main__menu-item">
     HeadingText
     </a>
    </li>
    ```

2. Tags and content on separate lines
3. Order according to Markdown

___

## OUTPUT FORMAT

- Return HTML only
- No Markdown
- No comments

___

## EXAMPLE (ONE SHOT)

### Input HTML CONTENT

'''
{html_example}
'''

### Output HTML MENU

'''
{html_menu_example}
'''