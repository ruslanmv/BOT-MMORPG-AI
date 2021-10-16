cnt = 1
while(1):
    ret, frame = cap.read()
    fgmask = fgbg.apply(frame)
    cv2.imshow('frame',fgmask)

    cv2.imwrite("frame" + str(cnt) + ".jpg", fgmask)
    cnt += 1