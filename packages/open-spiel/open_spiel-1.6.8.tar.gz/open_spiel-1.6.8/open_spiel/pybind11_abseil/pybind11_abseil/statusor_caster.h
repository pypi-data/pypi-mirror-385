// Author: Ken Oslund (kenoslund@)
#ifndef PYBIND11_ABSEIL_STATUSOR_CASTER_H_
#define PYBIND11_ABSEIL_STATUSOR_CASTER_H_

#include <pybind11/pybind11.h>

#include <stdexcept>
#include <type_traits>
#include <utility>

#include "absl/status/status.h"
#include "absl/status/statusor.h"
#include "pybind11_abseil/check_status_module_imported.h"
#include "pybind11_abseil/no_throw_status.h"
#include "pybind11_abseil/status_caster.h"

namespace pybind11 {
namespace detail {

template <typename PayloadType>
struct NoThrowStatusType<absl::StatusOr<PayloadType>> {
  using NoThrowAbslStatus = type_caster_base<absl::Status>;
  static constexpr auto name = _("Union[") + NoThrowAbslStatus::name + _(", ") +
                               make_caster<PayloadType>::name + _("]");
};

// Convert absl::StatusOr<T>.
// It isn't possible to specify separate return value policies for the container
// (StatusOr) and the payload. Since StatusOr is processed and not ever actually
// represented in python, the return value policy applies to the payload. Eg, if
// you return a StatusOr<MyObject*> (note the * is inside the StatusOr) with a
// take_ownership return val policy and the status is ok (ie, it has a payload),
// python will take ownership of that payload and free it when it is garbage
// collected.
// However, if you return a StatusOr<MyObject>* (note the * is outside the
// StatusOr rather than inside it now) with a take_ownership return val policy,
// python does not take ownership of the StatusOr and will not free it (because
// again, that policy applies to MyObject, not StatusOr).
template <typename PayloadType>
struct type_caster<absl::StatusOr<PayloadType>> {
 public:
  using PayloadCaster = make_caster<PayloadType>;
  using StatusCaster = make_caster<absl::Status>;

  PYBIND11_TYPE_CASTER(absl::StatusOr<PayloadType>, PayloadCaster::name);

  // We need this to support overriding virtual functions in Python. See the
  // test cases for example.
  bool load(handle /*src*/, bool /*convert*/) {
    // This will not be called as long as we do not call C++ functions that
    // redirect virtual calls back to Python.
    // TODO(wangxf): Implement the load function.
    return false;
  }

  // Convert C++ -> Python.
  static handle cast(const absl::StatusOr<PayloadType>* src,
                     return_value_policy policy, handle parent,
                     bool throw_exception = true) {
    if (!src) return none().release();
    return cast_impl(*src, policy, parent, throw_exception);
  }

  static handle cast(const absl::StatusOr<PayloadType>& src,
                     return_value_policy policy, handle parent,
                     bool throw_exception = true) {
    return cast_impl(src, policy, parent, throw_exception);
  }

  static handle cast(absl::StatusOr<PayloadType>&& src,
                     return_value_policy policy, handle parent,
                     bool throw_exception = true) {
    return cast_impl(std::move(src), policy, parent, throw_exception);
  }

 private:
  template <typename CType>
  static handle cast_impl(CType&& src, return_value_policy policy,
                          handle parent, bool throw_exception) {
    google::internal::CheckStatusModuleImported();
    if (src.ok()) {
      // Convert and return the payload.
      return PayloadCaster::cast(std::forward<CType>(src).value(), policy,
                                 parent);
    } else {
      // Convert and return the error.
      return StatusCaster::cast(std::forward<CType>(src).status(),
                                return_value_policy::move, parent,
                                throw_exception);
    }
  }
};

}  // namespace detail
}  // namespace pybind11

#endif  // PYBIND11_ABSEIL_STATUSOR_CASTER_H_
