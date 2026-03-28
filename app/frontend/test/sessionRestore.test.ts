import assert from "node:assert/strict";

import { shouldRestoreSavedSession } from "../src/components/chat/sessionRestore.js";

assert.equal(
  shouldRestoreSavedSession({ exists: true, messages: [] }),
  true,
);

assert.equal(
  shouldRestoreSavedSession({ exists: false, messages: [] }),
  false,
);
