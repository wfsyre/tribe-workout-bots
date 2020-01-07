import slack_api

def main():
    custom_emoji_file = open("custom_emoji_names.txt", "r")
    sample_output = open("sample.txt", "w")
    emoji_json = slack_api.get_emojis()['emoji']
    for line in custom_emoji_file:
        b = line.strip()
        b = b.strip(":")
        print(b)
        sample_output.write("  - name: " + b)
        sample_output.write("\n    src: \"" + emoji_json[b] + "\"\n")
    sample_output.close()
    custom_emoji_file.close()

if __name__ == '__main__':
    main()