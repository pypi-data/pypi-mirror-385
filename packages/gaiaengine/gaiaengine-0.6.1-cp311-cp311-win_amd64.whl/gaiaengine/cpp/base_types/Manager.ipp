#pragma once

template <DerivedFromManagedElement T>
std::shared_ptr<T> Manager<T>::createElement(const py::object& myClass, const py::args& args /*= py::args()*/) {
  py::object pyElement = py::object(myClass(*(py::make_tuple(this) + args)));
  
  std::shared_ptr<T> newElement = pyElement.cast<std::shared_ptr<T>>();
  
  setPythonObjectToKeepAlive(newElement, pyElement);

  setLocationInManager(newElement, _managedElementsPendingAdd.size());
  _managedElementsPendingAdd.push_back(newElement);

  return newElement;
}

template <DerivedFromManagedElement T>
std::shared_ptr<T> Manager<T>::createElementAt(const py::object& myClass, int index, const py::args& args /*= py::args()*/) {
  std::shared_ptr<T> addedElement = createElement(myClass, args);
  addedElement->setRequestedInitialIndex(index);
  
  return addedElement;
}


template <DerivedFromManagedElement T>
std::vector<std::shared_ptr<T>> Manager<T>::getElementsByFilter(const std::function<bool(const std::shared_ptr<T>)>& filter) {
  std::vector<std::shared_ptr<T>> result;

  processElementsPendingUpdates();

  for (auto& element : _managedElements) {
    if (filter(element)) {
      result.push_back(element);
    }
  }

  return result;
}

template <DerivedFromManagedElement T>
std::vector<std::shared_ptr<ManagedElement>> Manager<T>::getManagedElementsByFilter(const std::function<bool(const std::shared_ptr<ManagedElement>)>& filter) {
  std::vector<std::shared_ptr<ManagedElement>> result;

  processElementsPendingUpdates();

  for (auto& element : _managedElements) {
    if (filter == nullptr || filter(element)) {
      result.push_back(element);
    }
  }

  return result;
}

template <DerivedFromManagedElement T>
template <DerivedFromManagedElement U>
std::shared_ptr<U> Manager<T>::getElementByClass() {
  processElementsPendingUpdates();

  for (auto& element : _managedElements) {
    if (std::shared_ptr<U> castElement = std::dynamic_pointer_cast<U>(element))
      return castElement;
  }

  return nullptr;
}

template <DerivedFromManagedElement T>
void Manager<T>::deleteElement(size_t index, bool isPendingAdd) {
  if (isPendingAdd) {
    _managedElementsPendingAdd[index].reset();
    _managedElementsPendingAddDirty = true;
  }
  else {
    _managedElements[index].reset();
    _managedElementsDirty = true;
  }
}

template <DerivedFromManagedElement T>
void Manager<T>::processElementsPendingUpdates() {
  if (_managedElementsDirty) {
    int lastCleanIndex = 0;
    for (int i = 0; i < _managedElements.size(); i++) {
      if (_managedElements[i].get()) {
        _managedElements[lastCleanIndex] = _managedElements[i];
        setLocationInManager(_managedElements[lastCleanIndex], lastCleanIndex);
        lastCleanIndex++;
      }
    }
    _managedElements.resize(lastCleanIndex);
    _managedElementsDirty = false;
  }

  if (_managedElementsPendingAddDirty) {
    int lastCleanIndex = 0;
    for (int i = 0; i < _managedElementsPendingAdd.size(); i++) {
      if (_managedElementsPendingAdd[i].get()) {
        _managedElementsPendingAdd[lastCleanIndex] = _managedElementsPendingAdd[i];
        setLocationInManager(_managedElementsPendingAdd[lastCleanIndex], lastCleanIndex);
        lastCleanIndex++;
      }
    }
    _managedElementsPendingAdd.resize(lastCleanIndex);
    _managedElementsPendingAddDirty = false;
  }

  // Adding the pending elements to the main array and updating their indices
  int managedElementsPreviousSize = (int)_managedElements.size();
  _managedElements.resize(managedElementsPreviousSize + _managedElementsPendingAdd.size());

  for (int i = 0; i < _managedElementsPendingAdd.size(); i++) {
    setIsPendingAdd(_managedElementsPendingAdd[i], false);
    int requestedInitialIndex = _managedElementsPendingAdd[i]->getRequestedInitialIndex();
    
    if (requestedInitialIndex < 0 || requestedInitialIndex >= managedElementsPreviousSize + i) {
      setLocationInManager(_managedElementsPendingAdd[i], managedElementsPreviousSize + i);
      _managedElements[managedElementsPreviousSize + i] = _managedElementsPendingAdd[i];
    }

    else {
      // Offset all elements before adding the new one at the right place
      for (int j = managedElementsPreviousSize + i; j > requestedInitialIndex; j--) {
        _managedElements[j] = _managedElements[j - 1];
        setLocationInManager(_managedElements[j], j);
      }

      _managedElements[requestedInitialIndex] = _managedElementsPendingAdd[i];
      setLocationInManager(_managedElements[requestedInitialIndex], requestedInitialIndex);
    }
  }
  _managedElementsPendingAdd.clear();
}

