//
// Created by haridev on 2/14/22.
//

#ifndef CPPLOGGER_LOGGER_H
#define CPPLOGGER_LOGGER_H

#include <cstdarg>
#include <memory>
#include <unordered_map>
#include <string>

namespace cpplogger {
enum LoggerType {
  NO_LOG = 0,
  LOG_PRINT = 1,
  LOG_ERROR = 2,
  LOG_WARN = 3,
  LOG_INFO = 4,
  LOG_DEBUG = 5,
  LOG_TRACE = 6,
};

class Logger {
 private:
  std::string _app_name;
  FILE *_file;
  static std::unordered_map<std::string, std::shared_ptr<Logger>> instance_map;

 public:
  LoggerType level;

  explicit Logger(std::string app_name, FILE *file = stdout)
      : _app_name(app_name), _file(file), level(LoggerType::LOG_ERROR) {}

  static std::shared_ptr<Logger> Instance(std::string app_name = "LOGGER", FILE *file = stdout) {
    auto iter = instance_map.find(app_name);
    std::shared_ptr<Logger> instance;
    if (iter == instance_map.end()) {
      instance = std::make_shared<Logger>(app_name, file);
      instance_map.emplace(app_name, instance);
    } else {
      instance = iter->second;
    }
    return instance;
  }

  void log(LoggerType type, const char *string, ...) {
    va_list args;
    va_start(args, string);
    char buffer[4096];
    int resu = vsprintf(buffer, string, args);
    (void)resu;
    switch (type) {
      case LoggerType::LOG_PRINT: {
        if (level >= LoggerType::LOG_PRINT) {
          fprintf(_file, "[%s PRINT]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      case LoggerType::LOG_TRACE: {
        if (level >= LoggerType::LOG_TRACE) {
          fprintf(_file, "[%s TRACE]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      case LoggerType::LOG_DEBUG: {
        if (level >= LoggerType::LOG_DEBUG) {
          fprintf(_file, "[%s DEBUG]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      case LoggerType::LOG_INFO: {
        if (level >= LoggerType::LOG_INFO) {
          fprintf(_file, "[%s INFO]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      case LoggerType::LOG_WARN: {
        if (level >= LoggerType::LOG_WARN) {
          fprintf(_file, "[%s WARN]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      case LoggerType::LOG_ERROR: {
        if (level >= LoggerType::LOG_ERROR) {
          fprintf(_file, "[%s ERROR]: %s\n", _app_name.c_str(), buffer);
          fflush(_file);
        }
        break;
      }
      default: {
          break;
      }
    }

    va_end(args);
  }
};

}  // namespace cpplogger

#endif  // CPPLOGGER_LOGGER_H
