/** @odoo-module */
/* global QUnit */
/*
    Copyright 2025 Dixmit
    License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
*/
import {click} from "@web/../tests/utils";
import {start} from "@mail/../tests/helpers/test_utils";
import {startServer} from "@bus/../tests/helpers/mock_python_environment";

QUnit.module("ai_oca_bridge");

QUnit.test("AI Notification", async function (assert) {
    const pyEnv = await startServer();
    const resPartnerId1 = pyEnv["res.partner"].create({
        ai_bridge_info: [
            {name: "AI 1", id: 1, description: "test1 description"},
            {name: "AI 2", id: 2},
        ],
    });
    const views = {
        "res.partner,false,form": `<form>
                <field name="ai_bridge_info" />
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>`,
    };

    const {openView} = await start({serverData: {views}});
    await openView({
        res_id: resPartnerId1,
        res_model: "res.partner",
        views: [[false, "form"]],
    });

    await new Promise((resolve) => setTimeout(resolve, 1000));
    await assert.strictEqual(
        document.querySelectorAll(`.o_ChatterTopbar_AIButton .ai_button_selection`)
            .length,
        1,
        "should have an AI button"
    );

    await click(".o_ChatterTopbar_AIButton .ai_button_selection");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    assert.strictEqual(
        document.querySelectorAll(`.o_ChatterTopbar_AIItem`).length,
        2,
        "should have 2 AI Items"
    );

    await click(".dropdown-item:first-child");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    assert.strictEqual(
        document.querySelectorAll(`.o_notification_manager .o_notification`).length,
        1,
        "should have 1 Notification after clicking on AI Item"
    );
});

QUnit.test("AI Action", async (assert) => {
    console.log("Starting AI Action test...");
    const pyEnv = await startServer();
    const resPartnerId1 = pyEnv["res.partner"].create({
        ai_bridge_info: [
            {name: "AI 1", id: 1, description: "test1 description"},
            {name: "AI 2", id: 2},
        ],
    });

    const views = {
        "res.partner,false,form": `<form>
                <field name="ai_bridge_info" />
                <div class="oe_chatter">
                    <field name="message_follower_ids"/>
                    <field name="message_ids"/>
                </div>
            </form>`,
        "res.partner,false,tree": `<tree>
                <field name="name"/>
                <field name="active"/>
            </tree>`,
    };

    const {openView} = await start({serverData: {views}});
    await openView({
        res_id: resPartnerId1,
        res_model: "res.partner",
        views: [[false, "form"]],
    });

    await new Promise((resolve) => setTimeout(resolve, 1000));
    await assert.strictEqual(
        document.querySelectorAll(`.o_ChatterTopbar_AIButton .ai_button_selection`)
            .length,
        1,
        "should have an AI button"
    );

    await click(".o_ChatterTopbar_AIButton .ai_button_selection");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    assert.strictEqual(
        document.querySelectorAll(`.o_ChatterTopbar_AIItem`).length,
        2,
        "should have 2 AI Items"
    );

    await click(".dropdown-item:nth-child(2)");
    await new Promise((resolve) => setTimeout(resolve, 1000));
    assert.strictEqual(
        document.querySelectorAll(`.o_list_view`).length,
        1,
        "should have 1 List View after clicking on AI Item with action"
    );
});
