import hashlib
from datetime import datetime

import d_fake_seeder.domain.torrent.bencoding as bencoding
import d_fake_seeder.lib.util.helpers as helpers
from d_fake_seeder.lib.logger import logger


class File:
    def __init__(self, filepath):
        logger.info("File Startup", extra={"class_name": self.__class__.__name__})
        while True:
            try:
                self.filepath = filepath
                f = open(filepath, "rb")
                self.raw_torrent = f.read()
                f.close()
                self.torrent_header = bencoding.decode(self.raw_torrent)

                if b"announce" in self.torrent_header:
                    self.announce = self.torrent_header[b"announce"].decode("utf-8")

                if b"announce-list" in self.torrent_header:
                    announce_list = self.torrent_header[b"announce-list"]
                    if isinstance(announce_list, list):
                        # Extract announce URLs from the announce-list
                        announce_urls = [url.decode("utf-8") for sublist in announce_list for url in sublist]
                        self.announce_list = announce_urls

                torrent_info = self.torrent_header[b"info"]
                m = hashlib.sha1()
                m.update(bencoding.encode(torrent_info))
                self.file_hash = m.digest()
                break
            except Exception as e:
                logger.info(
                    "File read error: " + str(e),
                    extra={"class_name": self.__class__.__name__},
                )

    @property
    def total_size(self):
        logger.debug("File size", extra={"class_name": self.__class__.__name__})
        size = 0
        torrent_info = self.torrent_header[b"info"]
        if b"files" in torrent_info:
            # Multiple File Mode
            for file_info in torrent_info[b"files"]:
                size += file_info[b"length"]
        else:
            # Single File Mode
            size = torrent_info[b"length"]

        return size

    @property
    def name(self):
        logger.debug("File name", extra={"class_name": self.__class__.__name__})
        torrent_info = self.torrent_header[b"info"]
        return torrent_info[b"name"].decode("utf-8")

    def __str__(self):
        logger.debug("File attribute", extra={"class_name": self.__class__.__name__})
        announce = self.torrent_header[b"announce"].decode("utf-8")
        result = "Announce: %s\n" % announce

        if b"creation date" in self.torrent_header:
            try:
                creation_date = self.torrent_header[b"creation date"]
                creation_date = datetime.fromtimestamp(creation_date)
                result += "Date: %s\n" % creation_date.strftime("%Y/%m/%d %H:%M:%S")
            except (TypeError, ValueError, OSError):
                # Invalid creation date, skip it
                pass

        if b"created by" in self.torrent_header:
            created_by = self.torrent_header[b"created by"].decode("utf-8")
            result += "Created by: %s\n" % created_by

        if b"encoding" in self.torrent_header:
            encoding = self.torrent_header[b"encoding"].decode("utf-8")
            result += "Encoding:   %s\n" % encoding

        torrent_info = self.torrent_header[b"info"]
        piece_len = torrent_info[b"piece length"]
        result += "Piece len: %s\n" % helpers.sizeof_fmt(piece_len)
        pieces = len(torrent_info[b"pieces"]) / 20
        result += "Pieces: %d\n" % pieces

        torrent_name = torrent_info[b"name"].decode("utf-8")
        result += "Name: %s\n" % torrent_name
        piece_len = torrent_info[b"piece length"]

        if b"files" in torrent_info:
            # Multiple File Mode
            result += "Files:\n"
            for file_info in torrent_info[b"files"]:
                fullpath = "/".join([x.decode("utf-8") for x in file_info[b"path"]])
                result += "  '%s' (%s)\n" % (
                    fullpath,
                    helpers.sizeof_fmt(file_info[b"length"]),
                )
        else:
            # Single File Mode
            result += "Length: %s\n" % helpers.sizeof_fmt(torrent_info[b"length"])
            if b"md5sum" in torrent_info:
                result += "Md5: %s\n" % torrent_info[b"md5sum"]

        return result

    def get_announce(self):
        return self.torrent_header[b"announce"].decode("utf-8")

    def get_creation_date(self):
        if b"creation date" in self.torrent_header:
            try:
                creation_date = self.torrent_header[b"creation date"]
                creation_date = datetime.fromtimestamp(creation_date)
                return creation_date.strftime("%Y/%m/%d %H:%M:%S")
            except (TypeError, ValueError, OSError):
                # Invalid creation date (wrong type, out of range, etc.)
                return None
        return None

    def get_created_by(self):
        if b"created by" in self.torrent_header:
            return self.torrent_header[b"created by"].decode("utf-8")
        return None

    def get_encoding(self):
        if b"encoding" in self.torrent_header:
            return self.torrent_header[b"encoding"].decode("utf-8")
        return None

    def get_comment(self):
        """Get torrent comment"""
        if b"comment" in self.torrent_header:
            return self.torrent_header[b"comment"].decode("utf-8", errors="ignore")
        return None

    def get_piece_length(self):
        """Get piece length in bytes"""
        torrent_info = self.torrent_header[b"info"]
        return torrent_info.get(b"piece length", 0)

    def get_piece_count(self):
        """Get total number of pieces"""
        torrent_info = self.torrent_header[b"info"]
        if b"pieces" in torrent_info:
            return len(torrent_info[b"pieces"]) // 20
        return 0

    def get_info_hash_hex(self):
        """Get info hash as hexadecimal string"""
        return self.file_hash.hex()

    def is_private(self):
        """Check if torrent is private"""
        torrent_info = self.torrent_header[b"info"]
        return torrent_info.get(b"private", 0) == 1

    def get_file_list(self):
        """Get list of files in the torrent"""
        torrent_info = self.torrent_header[b"info"]
        files = []

        if b"files" in torrent_info:
            # Multi-file torrent
            for file_info in torrent_info[b"files"]:
                path_parts = [part.decode("utf-8", errors="ignore") for part in file_info[b"path"]]
                files.append(
                    {
                        "path": "/".join(path_parts),
                        "size": file_info[b"length"],
                        "size_formatted": helpers.sizeof_fmt(file_info[b"length"]),
                    }
                )
        else:
            # Single file torrent
            files.append(
                {
                    "path": torrent_info[b"name"].decode("utf-8", errors="ignore"),
                    "size": torrent_info[b"length"],
                    "size_formatted": helpers.sizeof_fmt(torrent_info[b"length"]),
                }
            )

        return files

    def get_trackers(self):
        """Get all tracker URLs"""
        trackers = []

        # Primary announce
        if b"announce" in self.torrent_header:
            trackers.append(self.torrent_header[b"announce"].decode("utf-8", errors="ignore"))

        # Announce list
        if hasattr(self, "announce_list"):
            for url in self.announce_list:
                if url not in trackers:
                    trackers.append(url)

        return trackers

    def get_num_pieces(self):
        return len(self.torrent_header[b"info"][b"pieces"]) / 20

    def get_torrent_name(self):
        return self.torrent_header[b"info"][b"name"].decode("utf-8")

    def get_files(self):
        files = []
        if b"files" in self.torrent_header[b"info"]:
            for file_info in self.torrent_header[b"info"][b"files"]:
                fullpath = "/".join([x.decode("utf-8") for x in file_info[b"path"]])
                # Return raw byte length for consistent formatting by UI components
                files.append((fullpath, file_info[b"length"]))
        return files

    def get_single_file_info(self):
        if b"files" not in self.torrent_header[b"info"]:
            # Return raw byte length for consistent formatting by UI components
            return self.torrent_header[b"info"][b"length"]
        return None

    def get_md5sum(self):
        if b"md5sum" in self.torrent_header[b"info"]:
            return self.torrent_header[b"info"][b"md5sum"]
        return None
