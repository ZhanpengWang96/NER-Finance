while (1):
    print('Please input your sentence:')
    demo_sent = input()
    if demo_sent == '' or demo_sent.isspace():
        print('See you next time!')
        break
    else:
        demo_sent = list(demo_sent.strip())
        demo_data = [(demo_sent, ['O'] * len(demo_sent))]
        print(demo_data)