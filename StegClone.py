import cv2
import numpy as np
import argparse
import pyfiglet

from os import path
from itertools import product


def xor(data, key):
    index = 0
    for i, j in product(range(data.shape[0]), range(data.shape[1])):
        for channel in range(3):
            data[i, j, channel] = data[i, j, channel] ^ ord(key[index % len(key)])
            index += 1

    return data


def embed(cover_image_path, secret_image_path, output_path, xor_key):

    try:

        cover_image = cv2.imread(cover_image_path)
        secret_image = cv2.imread(secret_image_path)

        # Resize the secret image to match the size of the cover image
        secret_image_resized = cv2.resize(secret_image, (cover_image.shape[1], cover_image.shape[0]))

        secret_image_xor = xor( secret_image_resized, xor_key )

        cover_channels = cv2.split(cover_image)

        # LSB Technique
        stego_channels = []
        for channel, secret_channel in zip(cover_channels, cv2.split(secret_image_xor)):
            lsb_cover = channel & 0xFE
            msb_secret = secret_channel >> 7
            stego_channel = lsb_cover | msb_secret
            stego_channels.append(stego_channel)

        # Merge the stego color channels
        stego_image = cv2.merge(stego_channels)
        cv2.imwrite(output_path, stego_image)

        print("[+] Embedding performed. Path to file:\n[+] " + path.abspath(output_path))

    except Exception as exp:
        print("[-] Embedding failed. Error:", str(exp))


def decode(stego_image_path, output_path, xor_key):

    try:
        stego_image = cv2.imread(stego_image_path)

        stego_channels = cv2.split(stego_image)

        secret_channels = []

        # Reverse LSB Technique
        for stego_channel in stego_channels:
            lsb_stego = stego_channel & 0x01
            secret_channel = lsb_stego << 7
            secret_channels.append(secret_channel)
    
        secret_xor_image = cv2.merge(secret_channels)

        # Xor Decryption
        secret_image = xor(secret_xor_image, xor_key)

        cv2.imwrite(output_path, secret_image)

        print("[+] Decoding performed. Path to file:\n[+] " + path.abspath(output_path))

    except Exception as exp:
        print("[-] Decoding failed. Error:", str(exp))



def main():
    # Banner for fun
    ascii_banner = pyfiglet.figlet_format("StegClone")
    print(ascii_banner)

    parser = argparse.ArgumentParser(description='Steghide copy for rudimentary steganography \
                                     demonstration :) <School project>')
    parser.add_argument('action', choices=['embed', 'decode'], help='Action to perform: \
                        "embed" to embed a secret image or "decode" to retrieve a secret image')
    parser.add_argument('image_path', help='Path to the cover image to embed the secret image in \
                        or the stego image to retrieve the secret image from')
    parser.add_argument('secret_path', nargs='?', help='Path to the secret image to embed in the \
                        cover image (only used when "embed" action is selected)')
    parser.add_argument('--key', default='changeMe123', help='Encryption key (default: "changeMe123")')
    parser.add_argument('--output' , help="Output for the result")

    args = parser.parse_args()

    if args.action == 'embed':
        if args.secret_path is None:
            print("[-] Secret Path Missing... Exiting")
            return

        if args.key == "changeMe123":
            print("[!] WARNING: Encryption is performed with the default key.\n[!] Consider changing the key, as it can be found on the public repo.\n\n\n")

        if args.output is None:
            embed( args.image_path, args.secret_path, 'example_images/stego_image.png', args.key )
        else:
            embed( args.image_path, args.secret_path, args.output, args.key )

    if args.action == 'decode':
        if args.output is None:
            decode(args.image_path, 'example_images/decoded.png', args.key )
        else:
            decode(args.image_path, args.output )



if __name__ == "__main__":
    main()