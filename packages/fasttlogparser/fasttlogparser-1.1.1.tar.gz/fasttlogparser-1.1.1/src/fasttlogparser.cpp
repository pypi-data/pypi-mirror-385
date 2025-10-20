// Copyright 2025 Anton Bogdanov

#include <pybind11/numpy.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#define MAVLINK_USE_MESSAGE_INFO
#include <mavlink.h>
#include <mavlink_helpers.h>

#include <cstdint>
#include <fstream>
#include <iostream>
#include <map>
#include <memory>
#include <set>
#include <string>
#include <utility>
#include <vector>
#include <filesystem>  // NOLINT(build/c++17)
#if defined(_MSC_VER)
  #include <locale>
  #include <codecvt>
#endif
#include <MessageSeries.h>


uint64_t swapThis(uint64_t value) {
#if defined(_MSC_VER)
  return _byteswap_uint64(value);
#else
  return __builtin_bswap64(value);
#endif
}

namespace py = pybind11;

std::vector<char> readFile(const std::string &utf8_path) {
#if defined(_MSC_VER)
  std::wstring_convert<std::codecvt_utf8_utf16<wchar_t>> converter;
  std::wstring wide_path = converter.from_bytes(utf8_path);
#else
  std::string wide_path = utf8_path;
#endif

  std::error_code ec;
  auto size = std::filesystem::file_size(wide_path, ec);
  if (ec) {
    throw std::runtime_error("Error getting file size!");
  }

  std::ifstream file(wide_path, std::ios::binary | std::ios::in);
  std::vector<char> buffer(size);
  if (file.read(buffer.data(), size)) {
    return buffer;
  } else {
    throw std::runtime_error("Error while file read!");
  }
}

using MavId = std::pair<uint8_t, uint8_t>;
bool filterMsgById(std::vector<MavId> ids, mavlink_message_t *msg) {
  if (ids.size() == 0) {
    return false;
  }

  for (auto id : ids) {
    if (id.first == msg->sysid && id.second == msg->compid) {
      return false;
    }
  }

  return true;
}

bool filterMsgByBlackList(std::set<std::string> whitelist,
                          std::set<std::string> backlist,
                          mavlink_message_t *msg) {
  const mavlink_message_info_t *msg_info = mavlink_get_message_info(msg);
  std::string msg_name(msg_info->name);

  if (whitelist.size() != 0) {
    if (whitelist.find(msg_name) == whitelist.end()) {
      return true;
    }
  }

  if (backlist.find(msg_name) != backlist.end()) {
    return true;
  }

  return false;
}

using MavIds = std::map<uint8_t, std::set<uint8_t>>;
void addMavId(MavIds &ids, mavlink_message_t *msg) {
  auto pair = ids.find(msg->sysid);
  if (pair != ids.end()) {
    pair->second.insert(msg->compid);
  } else {
    ids.insert({msg->sysid, std::set<uint8_t>({msg->compid})});
  }
}

using FieldsMap = std::map<std::string, py::array>;
using MessagesMap = std::map<std::string, FieldsMap>;

std::pair<MessagesMap, MavIds>
parseTLog(const std::string &path, std::optional<std::vector<MavId>> ids_opt,
          std::optional<std::vector<std::string>> whitelist_opt,
          std::optional<std::vector<std::string>> blacklist_opt,
          std::optional<std::map<std::string, std::string>> remap_field_opt) {
  std::vector<MavId> ids =
      ids_opt.has_value() ? ids_opt.value() : std::vector<MavId>();
  std::vector<std::string> whitelist = whitelist_opt.has_value()
                                           ? whitelist_opt.value()
                                           : std::vector<std::string>();
  std::vector<std::string> blacklist = blacklist_opt.has_value()
                                           ? blacklist_opt.value()
                                           : std::vector<std::string>();
  std::map<std::string, std::string> remap_field =
      remap_field_opt.has_value() ? remap_field_opt.value()
                                  : std::map<std::string, std::string>();

  std::set<std::string> whitelist_set(whitelist.begin(), whitelist.end());
  std::set<std::string> blacklist_set(blacklist.begin(), blacklist.end());

  std::vector<char> data = readFile(path);
  std::map<std::string, std::shared_ptr<MessageSeries>> series_map;
  MavIds found_ids;

  mavlink_status_t status = {0};
  mavlink_message_t msg;
  int chan = MAVLINK_COMM_0;
  uint64_t timestamp = 0;

  for (size_t i = sizeof(uint64_t); i < data.size(); ++i) {
    uint8_t byte = data[i];
    uint8_t framing_result = mavlink_frame_char(chan, byte, &msg, &status);

    if (status.parse_state == MAVLINK_PARSE_STATE_GOT_STX) {
      timestamp = swapThis(
          *reinterpret_cast<uint64_t *>(data.data() + i - sizeof(uint64_t)));
    }

    if (framing_result == MAVLINK_FRAMING_OK) {
      i += sizeof(uint64_t);
      addMavId(found_ids, &msg);
      if (filterMsgById(ids, &msg)) {
        continue;
      }
      if (filterMsgByBlackList(whitelist_set, blacklist_set, &msg)) {
        continue;
      }

      const mavlink_message_info_t *msg_info = mavlink_get_message_info(&msg);
      if (!msg_info) {
        continue;
      }

      std::string msg_name(msg_info->name);
      auto pair = series_map.find(msg_name);
      if (pair != series_map.end()) {
        pair->second->addMsg(timestamp, &msg);
      } else {
        auto series = std::make_shared<MessageSeries>(msg_info);
        series->addMsg(timestamp, &msg);
        series_map.insert({msg_name, series});
      }
    } else if (framing_result == MAVLINK_FRAMING_BAD_CRC) {
      py::print("BAD_CRC: msg id", static_cast<int>(msg.msgid));
    } else if (framing_result == MAVLINK_FRAMING_BAD_SIGNATURE) {
      py::print("BAD_SIGNATURE: msg id", static_cast<int>(msg.msgid));
    }
  }

  MessagesMap msg_map;
  for (auto pair : series_map) {
    msg_map.insert({pair.first, pair.second->getFields(remap_field)});
  }
  return std::pair{msg_map, found_ids};
}

PYBIND11_MODULE(fasttlogparser, m) {
  m.def("parseTLog", &parseTLog, py::arg("path"), py::arg("ids") = py::none(),
        py::arg("whitelist") = py::none(), py::arg("blacklist") = py::none(),
        py::arg("remap_field") = py::none());
#ifdef VERSION_INFO
  m.attr("__version__") = VERSION_INFO;
#else
  m.attr("__version__") = "dev";
#endif
}
