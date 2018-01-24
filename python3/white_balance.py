from PIL import Image
import numpy as np


def white_balance(channel, percentile=0.05):
    mi, ma = (np.percentile(channel, percentile), np.percentile(channel, 100.0 - percentile))
    channel = np.uint8(np.clip((channel - mi) * 255.0 / (ma - mi), 0, 255))
    return channel


def do_white_balance(image):
	fixed_channels = map(lambda channel: white_balance(channel, 1), image.split())
	a_fixed_image = np.dstack(fixed_channels)
	return Image.fromarray(np.uint8(a_fixed_image))


def main():
	image = Image.open('OLK_3399.jpg')
	do_white_balance(image).show()
	# do_white_balance(image).save('some_wb_06.jpg')


if __name__ == '__main__':
	main()
