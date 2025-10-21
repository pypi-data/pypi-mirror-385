#pragma once

#include <pybind11/pybind11.h>

#include <concepts>
#include <functional>
#include <memory>
#include <vector>

namespace py = pybind11;


class ManagerBase;
class Window;

class ManagedElement {
public:
  virtual ~ManagedElement() = default;

  virtual void deleteElement();
  inline std::shared_ptr<ManagerBase> getManager() const { return _manager.lock(); }
  inline bool isElementDeleted() const { return _isDeleted; }

  // Will be used when moving from the pending add managed element array to the main one 
  // to try and put it at the right place in the array. If not within bounds, puts at the end of the array
  int getRequestedInitialIndex() const { return _requestedInitialIndex; }
  void setRequestedInitialIndex(int val) { _requestedInitialIndex = val; }

  // Helper function for elements managed by Components
  // Raises an exception if not the case
  virtual std::shared_ptr<Window> getWindow() const;

  static void pythonBindings(py::module& m);

protected:
  ManagedElement(std::shared_ptr<ManagerBase> manager) : _manager(manager) {}

private:
  friend class ManagerBase;
  void setLocationInManager(size_t val) { _indexInManager = val; }
  void setIsPendingAdd(bool val) { _isPendingAdd = val; }
  void setPythonObjectToKeepAlive(py::object val) { _objectToKeepAlive = val; }

  std::weak_ptr<ManagerBase> _manager;
  size_t _indexInManager = 0;
  int _requestedInitialIndex = -1;
  bool _isPendingAdd = true;
  bool _isDeleted = false;
  py::object _objectToKeepAlive;
};


class ManagerBase {
public:
  virtual ~ManagerBase() = default;
  
  virtual std::shared_ptr<ManagedElement> createManagedElement(const py::object& myClass, const py::args& args = py::args()) = 0;
  virtual std::shared_ptr<ManagedElement> createManagedElementAt(const py::object& myClass, int index, const py::args& args = py::args()) = 0;
  virtual std::vector<std::shared_ptr<ManagedElement>> getManagedElementsByFilter(const std::function<bool(const std::shared_ptr<ManagedElement>)>& filter = nullptr) = 0;

  static void pythonBindings(py::module& m);

protected:
  friend class ManagedElement;
  virtual void deleteElement(size_t index, bool isPendingAdd) = 0;

  void setLocationInManager(std::shared_ptr<ManagedElement> element, size_t val) { element->setLocationInManager(val); }
  void setIsPendingAdd(std::shared_ptr<ManagedElement> element, bool val) { element->setIsPendingAdd(val); }
  void setPythonObjectToKeepAlive(std::shared_ptr<ManagedElement> element, py::object val) { element->setPythonObjectToKeepAlive(val); }
};


template <typename T>
concept DerivedFromManagedElement = std::is_base_of_v<ManagedElement, T>;

template <DerivedFromManagedElement T>
class Manager : public ManagerBase {
public:
  Manager() = default;
  virtual ~Manager() = default;

  // Doesn't add the new element directly to the main array of elements (see processElementsPendingUpdates),
  // so that if an element is created while iterating over the list, it won't invalidate the iterators
  virtual std::shared_ptr<T> createElement(const py::object& myClass, const py::args& args = py::args());
  // Any index not within the bounds of the array gets added at the end
  virtual std::shared_ptr<T> createElementAt(const py::object& myClass, int index, const py::args& args = py::args());

  // Guaranteed to return valid elements
  virtual std::vector<std::shared_ptr<T>> getElements() { processElementsPendingUpdates(); return _managedElements; }
  virtual std::vector<std::shared_ptr<T>> getElementsByFilter(const std::function<bool(const std::shared_ptr<T>)>& filter);

  template <DerivedFromManagedElement U>
  std::shared_ptr<U> getElementByClass();

private:
  // Adds pending elements and remove invalid ones
  void processElementsPendingUpdates();

  std::shared_ptr<ManagedElement> createManagedElement(const py::object& myClass, const py::args& args = py::args()) override {
    return std::static_pointer_cast<ManagedElement>(createElement(myClass, args));
  }

  std::shared_ptr<ManagedElement> createManagedElementAt(const py::object& myClass, int index, const py::args& args = py::args()) override {
    return std::static_pointer_cast<ManagedElement>(createElementAt(myClass, index, args));
  }

  std::vector<std::shared_ptr<ManagedElement>> getManagedElementsByFilter(const std::function<bool(const std::shared_ptr<ManagedElement>)>& filter) override;
  void deleteElement(size_t index, bool isPendingAdd) override;

  std::vector<std::shared_ptr<T>> _managedElements;
  std::vector<std::shared_ptr<T>> _managedElementsPendingAdd;
  bool _managedElementsDirty = false;
  bool _managedElementsPendingAddDirty = false;
};


class TestManagedElement : public ManagedElement {
public:
  TestManagedElement(std::shared_ptr<ManagerBase> manager) : ManagedElement(manager) {}

  static void pythonBindings(py::module& m);
};


class TestManager : public Manager<TestManagedElement> {
public:
  static void pythonBindings(py::module& m);
};

#include "Manager.ipp"
