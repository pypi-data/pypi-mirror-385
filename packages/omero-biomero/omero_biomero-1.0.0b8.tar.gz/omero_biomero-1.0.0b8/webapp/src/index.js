import ReactDOM from "react-dom/client";
import {
  BrowserRouter,
  Routes,
  Route,
  useSearchParams,
  useNavigate,
} from "react-router-dom";

import "./index.css";
import "./tailwind.css";
import { AppProvider } from "./AppContext";
import BiomeroApp from "./biomero/BiomeroApp";
import ImporterApp from "./importer/ImporterApp";
import {
  Navbar,
  NavbarGroup,
  NavbarHeading,
  NavbarDivider,
  Button,
} from "@blueprintjs/core";

const BiomeroIcon = () => (
  <div className="mr-2 w-[20px]">
    <svg
      viewBox="0 0 300 388"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="OMERO.biomero leaf–circuit icon"
    >
      <g transform="translate(0 388) scale(0.1 -0.1)" fill="currentColor">
        <path
          d="M1399 3578 c-155 -144 -445 -451 -555 -589 -248 -310 -407 -620 -458
-887 -49 -258 -16 -555 84 -769 107 -228 274 -394 578 -574 176 -104 249 -156
305 -219 53 -58 74 -114 83 -219 5 -52 13 -80 26 -93 41 -41 108 -7 108 55 0
29 37 69 427 454 291 287 433 420 443 416 73 -27 158 -2 202 59 33 47 33 159
0 206 -45 63 -134 88 -205 58 -71 -29 -123 -129 -102 -196 6 -20 -25 -55 -231
-261 -132 -132 -242 -239 -246 -239 -5 0 -8 109 -8 242 l0 242 277 278 278
278 46 0 c33 0 51 -6 64 -20 30 -33 98 -53 152 -45 86 13 155 112 139 198 -8
41 -41 93 -77 120 -34 24 -106 33 -152 18 -43 -15 -96 -71 -104 -112 -5 -28
-8 -29 -57 -29 l-51 0 -307 -307 c-168 -170 -312 -319 -319 -333 -11 -19 -15
-99 -17 -340 l-4 -315 -66 -70 c-37 -38 -70 -71 -74 -73 -5 -2 -8 227 -8 510
l0 513 424 424 c415 415 425 424 451 413 62 -28 154 0 199 61 32 43 30 159 -3
206 -27 37 -90 70 -135 71 -46 0 -115 -38 -142 -80 -20 -30 -25 -51 -25 -97
l0 -58 -377 -377 c-207 -208 -380 -378 -384 -378 -5 0 -8 99 -8 221 0 189 3
226 17 257 10 21 119 140 243 267 231 235 257 269 280 367 25 109 -2 228 -74
326 -44 59 -475 495 -508 513 -14 8 -39 -10 -129 -93z m358 -321 c204 -208
228 -244 228 -342 0 -49 -6 -82 -20 -110 -11 -22 -102 -124 -207 -230 l-187
-190 -1 523 c0 287 4 522 9 522 4 0 85 -78 178 -173z m-317 -315 c0 -258 -3
-523 -6 -589 l-7 -121 -59 64 c-73 78 -215 187 -323 249 -79 45 -105 54 -105
36 0 -6 97 -111 215 -235 139 -146 224 -244 242 -278 28 -52 28 -56 31 -262
l3 -210 -39 50 c-89 111 -257 257 -424 367 -138 91 -192 110 -156 55 9 -13
114 -124 233 -248 259 -268 316 -334 358 -420 l32 -65 3 -345 3 -345 -38 36
c-64 60 -112 93 -271 188 -375 222 -525 400 -604 719 -18 72 -22 117 -22 257
-1 182 5 225 56 385 74 235 206 461 421 720 76 91 436 460 449 460 4 0 8 -211
8 -468z m1104 -371 c26 -29 17 -73 -16 -85 -41 -15 -78 6 -78 43 0 56 58 82
94 42z m126 -599 c25 -20 30 -63 10 -87 -15 -18 -71 -20 -88 -3 -21 21 -15 75
10 92 29 20 41 20 68 -2z m-128 -619 c35 -32 10 -93 -39 -93 -25 0 -63 32 -63
53 0 48 65 74 102 40z"
        />
      </g>
    </svg>
  </div>
);

const AppRouter = () => {
  const [searchParams] = useSearchParams();
  const WEBCLIENT = window.WEBCLIENT;
  const { IMPORTER_ENABLED, ANALYZER_ENABLED } = WEBCLIENT.UI;
  const navigate = useNavigate();
  const appName =
    searchParams.get("tab") || (IMPORTER_ENABLED ? "import" : "biomero");

  return (
    <AppProvider>
      <div className="bg-[#f0f1f5] w-full h-full relative top-0">
        <Navbar className="z-[1] top-[35px]" fixedToTop>
          <NavbarGroup>
            {/* <Icon icon="style" className="mr-[7px]" /> */}
            <BiomeroIcon />
            <NavbarHeading>Biomero</NavbarHeading>
            <NavbarDivider />
            {IMPORTER_ENABLED && (
              <Button
                className={`bp5-minimal focus:ring-0 focus:ring-offset-0 ${
                  appName === "import"
                    ? "bp5-intent-primary font-bold shadow-md"
                    : ""
                }`}
                icon="cloud-upload"
                text="Import"
                onClick={() => navigate("?tab=import")}
                outlined={appName === "import"}
              />
            )}
            {ANALYZER_ENABLED && (
              <Button
                className={`bp5-minimal focus:ring-0 focus:ring-offset-0 ${
                  appName === "biomero"
                    ? "bp5-intent-primary font-bold shadow-md"
                    : ""
                }`}
                icon="data-sync"
                text="Analyze"
                onClick={() => navigate("?tab=biomero")}
                outlined={appName === "biomero"}
              />
            )}
          </NavbarGroup>
        </Navbar>
        <div className="pt-[50px]">
          {appName === "biomero" ? <BiomeroApp /> : <ImporterApp />}
        </div>
      </div>
    </AppProvider>
  );
};

window.onload = function () {
  const rootElement = document.getElementById("root");
  const root = ReactDOM.createRoot(rootElement);
  root.render(
    <BrowserRouter>
      <Routes>
        <Route path="*" element={<AppRouter />} />
      </Routes>
    </BrowserRouter>
  );
};
