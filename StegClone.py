import cv2
import numpy as np
import argparse
import pyfiglet


def embed(cover_image_path, secret_image_path, output_path):
    cover_image = cv2.imread(cover_image_path)
    secret_image = cv2.imread(secret_image_path)

    # Resize the secret image to match the size of the cover image
    secret_image_resized = cv2.resize(secret_image, (cover_image.shape[1], cover_image.shape[0]))

    cover_channels = cv2.split(cover_image)

    # LSB Technique
    stego_channels = []
    for channel, secret_channel in zip(cover_channels, cv2.split(secret_image_resized)):
        lsb_cover = channel & 0xFE
        msb_secret = secret_channel >> 7
        stego_channel = lsb_cover | msb_secret
        stego_channels.append(stego_channel)

    # Merge the stego color channels
    stego_image = cv2.merge(stego_channels)
    cv2.imwrite(output_path, stego_image)

    print("[+] Embedding performed.")


def decode(stego_image_path, output_path):
    # Load the stego image
    stego_image = cv2.imread(stego_image_path)

    # Extract the color channels of the stego image
    stego_channels = cv2.split(stego_image)

    # Create empty arrays for the secret image channels
    secret_channels = []

    # Extract the secret image channels using LSB steganography
    for stego_channel in stego_channels:
        lsb_stego = stego_channel & 0x01
        secret_channel = lsb_stego << 7
        secret_channels.append(secret_channel)

    # Merge the secret image channels
    secret_image = cv2.merge(secret_channels)

    # Save the secret image to the output file
    cv2.imwrite(output_path, secret_image)



def main():
    
    # Banner for fun
    ascii_banner = pyfiglet.figlet_format("StegClone")
    print(ascii_banner)

    parser = argparse.ArgumentParser(description='Steghide copy for rudimentary steganography demonstration :) <School project>')
    parser.add_argument('action', choices=['embed', 'decode'], help='Action to perform: "embed" to embed a secret image or "decode" to retrieve a secret image')
    parser.add_argument('image_path', help='Path to the cover image to embed the secret image in or the stego image to retrieve the secret image from')
    parser.add_argument('secret_path', nargs='?', help='Path to the secret image to embed in the cover image (only used when "embed" action is selected)')
    parser.add_argument('--key', default='changeMe123', help='Encryption key (default: "changeMe123")')
    parser.add_argument('--output' , help="Output for the result")
    # parser.add_argument('--')

    args = parser.parse_args()

    if args.action == 'embed':
        if args.secret_path is None:
            print("[-] Secret Path Missing... Exiting")
            return
        if args.output == None:
            embed( args.image_path, args.secret_path, 'stego_image.png' )
        else:
            embed( args.image_path, args.secret_path, args.output )

    if args.action == 'decode':
        if args.output == None:
            decode(args.image_path, 'decoded.png' )
        else:
            decode(args.image_path, args.output )



if __name__ == "__main__":
    main()